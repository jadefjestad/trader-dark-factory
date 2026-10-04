# Design: "high-frequency" paper trading on Alpaca, cheaply

Status: proposal, 2026-10-04. Nothing here is built or provisioned yet. Builds on
`docs/intraday-data.md` (#67) and refines backlog issues #3 and #69.

## 1. What "high frequency" can honestly mean here

True HFT (microsecond reactions, order-book queue position, co-location) is not possible on this
stack and no hosting choice changes that:

| Limit | Value on the free Alpaca plan | Consequence |
|---|---|---|
| Live data | IEX only, about 5% of consolidated volume; 30 symbols on the stream | Sparse prices at sub-minute scale; ~6% of minutes have no IEX trade at all |
| Trading API | about 200 requests a minute per account | At most ~3 order actions a second, shared by submits, cancels and REST polling |
| Fills | Simulated by Alpaca against the market, no queue, no market impact | Any edge that depends on queue position or passive fills is fictitious |
| Pattern-day-trader rule | Applies to paper accounts under $25k equity | Keep the paper account at its $100k default |
| Hosting latency | Azure East US to Alpaca is single-digit milliseconds | Irrelevant next to the limits above |

The realistic target is therefore a **streaming intraday tier**:

- Decisions every **5 seconds to 1 minute**, from bars the process builds itself off the live stream.
- Holding periods of **minutes to an hour**, flat by the close.
- At most a few orders a minute across the whole universe.
- A small universe for the sub-minute tier: the **5 to 10 most liquid names** (for example SPY, QQQ,
  AAPL, MSFT, NVDA), where IEX still prints often enough to form a price every few seconds.

Expectation to state up front: with a feed-mismatch charge of about 5 bps per trade (measured p95 in
#67) plus spread, a strategy trading on 5-second bars needs more than ~10 bps gross per round trip.
Most sub-minute ideas will fail the cost gates. That is a legitimate finding the ledger should record,
not a reason to weaken the gates. The tier's main value is faster, steadier execution of minute-level
strategies; sub-minute strategies are an experiment.

## 2. Where it runs

| Option | Monthly cost (list prices, check the Azure calculator) | Verdict |
|---|---|---|
| GitHub Actions long job (#3) | $0 on a public repo; on a private repo a full session daily is ~8,000 min vs 2,000 free | Fine for 15-minute bars once the repo is public. Can't stream all session (6-hour job cap, cron delays) |
| **Azure Container Apps, consumption plan**, 0.25 vCPU / 0.5 GiB, one replica during market hours only | about $0 (inside the monthly free grant) | **Recommended** |
| Same, one replica 24/7 | about $14 | Only if pre-market data warm-up turns out to matter |
| Azure B1s VM + small disk | about $8 to $10 | Works, but you patch the OS yourself |
| Azure Container Registry Basic | about $5 | Not needed: use GHCR (free; public once the repo is public) |
| Log Analytics | free up to 5 GB/month, then per GB | Keep platform logs minimal; decision logs go to Blob |
| Blob Storage for logs | cents | Yes |

Region: **East US**. Run the container as a **scheduled Container Apps Job** (start 09:20 ET, stop
16:10 ET, weekdays) rather than an always-on app, so it costs nothing outside market hours. If the
job's maximum run time turns out too short for a full session, fall back to an always-on app with
one replica (~$14).

What Jade would provision (unchanged from #69, plus one item):
1. One resource group with a Container Apps environment and the scheduled job.
2. One storage account with a `ledger-stream` container; the job writes to it with a managed
   identity (no secret).
3. Secrets on the job: the **paper** key ID and secret of a **second, dedicated paper account** (see 4.5).
4. A read-only SAS token for that blob container, stored as a GitHub secret `AZURE_LEDGER_SAS`, so
   an Actions job can copy the logs into the ledger.

No GitHub write credential ever lives in Azure.

## 3. Architecture

```
            Alpaca data websocket (IEX trades + quotes)      Alpaca paper trading API + trade_updates stream
                         │                                                   ▲            │
                         ▼                                                   │            ▼
 ┌──────────────── streamer container (deploy/streamer, #69) ─────────────────────────────────────┐
 │ feed ─► validator ─► bar builder (5s/15s/1m) ─► strategy sandbox ─► risk gate ─► order manager │
 │   │         │               │                     (child process,       │          │          │
 │   │         └── staleness / gap / crossed-quote checks (fail closed) ───┘          │          │
 │   └── heartbeat ─► /healthz                                       token bucket ◄───┘          │
 │                                     decision + order + fill log (JSON lines) ─► Azure Blob    │
 └────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                     │
   GitHub Actions (no Claude): nightly `stream-ledger` job copies Blob logs ─► ledger branch
                               15:50 ET `intraday-flatten` safety net (flattens the intraday account)
                               daily report reads heartbeat + fill quality
```

### 3.1 Feed and validation
- One websocket connection (Alpaca allows one per account on the free plan), subscribed to IEX
  trades and quotes for the universe.
- Every message is stamped with receive time. A symbol is **stale** if no trade or quote arrived in
  `max_stream_gap_seconds` (new risk limit, e.g. 30 s for the 5-second tier); the whole feed is stale if
  nothing arrived in 10 s during market hours.
- Reject crossed or locked quotes, zero or negative prices, and trades outside a sanity band around the
  last good price.
- Any failure means **no new orders** for that symbol (or all symbols if the feed is stale); existing
  positions are held, and flattened if the condition lasts past `stale_flatten_seconds`.

### 3.2 Bar builder
- Builds OHLCV bars plus last IEX bid/ask/mid at fixed boundaries (5 s, 15 s, 1 min), stamped with
  `start`, `end` and `available_at` (when the bar was closed locally), same convention as the #68
  backtester.
- An interval with no trade carries the previous close forward with volume 0 and a `filled=false`
  flag; strategies see the flag. A bar is never emitted early.

### 3.3 Strategy sandbox
- The current runner spawns a child process per evaluation, which is too slow every 5 seconds. The
  streamer instead starts **one long-lived child** at the open, under the same rules as
  `factory/runner.py`: private copy of code, empty environment, no network, separate OS user, allowed
  imports only.
- Protocol over a pipe: the parent sends the bar history (bounded window), the child returns one row of
  numeric target weights. Anything else (non-numeric, wrong length, timeout over 1 s) is treated as
  "hold" and logged; three in a row stops trading for the day.
- The strategy is the one in `state/champion_stream.json` (chosen by the evaluator and promoted by
  merge, never by Claude at runtime). The container pulls the champion at start from `main`.

### 3.4 Risk gate
Reads `protected/risk_limits.yaml` at start, plus a new `stream:` section:

| Limit | Suggested start value |
|---|---|
| `max_gross_exposure` | 0.5 of equity (lower than daily while unproven) |
| `max_position_weight` | 0.1 |
| `max_orders_per_minute` | 30 (well under the API's ~200 calls, leaving room for cancels and polling) |
| `max_orders_per_day` | 500 |
| `min_seconds_between_trades_per_symbol` | 30 |
| `max_daily_loss` | 1% of start-of-day equity: flatten and stop for the day |
| `max_stream_gap_seconds` | 30 |
| `flatten_at` | 15:55 ET |

The gate turns target weights into share deltas, drops deltas below a minimum notional, and refuses
anything that would breach a limit. Kill switch: env var `STREAM_KILL=1` or the existing kill switch in
the risk file flattens and exits.

### 3.5 Order manager
- Marketable orders only to start: market, or marketable limit at the far touch plus a cap of a few bps,
  `time_in_force=day`. Passive limit orders are left out because paper fills give them unrealistic
  queue priority.
- Deterministic `client_order_id` (`stream-<date>-<seq>`), so a restart never duplicates an order.
- Fills tracked from the `trade_updates` websocket; positions reconciled against REST every 60 s and
  after any reconnect. A mismatch the manager can't explain stops trading for the day.
- A token bucket enforces the order budget and keeps all REST calls under ~150 a minute.
- Every order logs the **expected price** (IEX mid at decision time) and the **fill price**; their
  difference is the live slippage the backtester's cost model is checked against.

### 3.6 Fail-closed summary
No orders when: keys missing, account number not `PA…`, endpoint not the paper URL, market clock
closed, feed or symbol stale, validation fails, sandbox misbehaves, a risk limit would be breached,
positions don't reconcile, daily loss limit hit, or anything raises. On any crash the container
restarts, re-reconciles, and resumes only if all checks pass. If the container is down entirely, the
15:50 ET Actions safety net flattens the intraday paper account.

## 4. Research side: backtesting the streaming tier

### 4.1 Data
- Historical **SIP trades and quotes** (free once older than 15 minutes) for the 5 to 10 tier symbols.
  Alpaca has no second-level bars, so a deterministic Actions job aggregates trades and quotes into
  5 s / 15 s bars and caches them as Parquet (GitHub Actions cache or a release asset; Blob if larger).
- Budget: SPY prints a few hundred thousand trades a day, so 60 sessions for 10 symbols is a few
  thousand requests per type, about an hour at the 200-a-minute limit. Run it once, then append daily.
- Same `available_at` stamping as #68.

### 4.2 Fill model (event-driven, conservative)
- Signal at bar close; order arrives after a **latency** drawn from 250 ms to 2 s; fills at the SIP ask
  (buys) or bid (sells) at arrival, plus the 5 bps feed-mismatch charge, plus fees.
- No passive fills, no price improvement. A partial-fill haircut on orders larger than a small share of
  the bar's volume.

### 4.3 Extra gates for the tier (new entries in `protected/evaluation.yaml`)
| Gate | Rule |
|---|---|
| `latency_robustness` | Sharpe at 2 s latency at least 70% of Sharpe at 250 ms |
| `cost_stress` | Already exists for 5Min/15Min; extend to the new timeframes at 2x costs |
| `order_budget` | Backtest never exceeds the `stream` order limits |
| `no_lookahead` | Unchanged: rerun on truncated data |
| `min_trades` | Scaled up for the shorter timeframe so a handful of lucky trades can't pass |

### 4.4 Promotion path
1. Evaluator passes all gates → candidate is promotable to `state/champion_stream.json`, but the new
   timeframe is **not** added to `executable_timeframes` yet.
2. **Shadow mode** for at least 10 sessions: the streamer runs the candidate, logs the orders it
   would place, and submits nothing. A nightly job compares shadow decisions with a replay of the
   backtester on the same day's data.
3. Live paper trading only after shadow and replay agree within tolerance (same trades, slippage
   inside the modelled band). That check is what adds the timeframe to `executable_timeframes`.
4. After going live, the daily report tracks paper fills vs model. If live slippage exceeds the model
   for 5 sessions running, the champion is demoted automatically.

### 4.5 A separate paper account
The daily champion and the streaming tier must not share positions. Alpaca allows more than one paper
account per login; the streamer uses its own, with its own key pair. This also makes the 15:50 safety
net safe: it flattens everything in that account and can never touch the daily strategy.

## 5. Build order

| Step | Where | Depends on | Needs from Jade |
|---|---|---|---|
| 0. Re-run `probe-sources` in market hours to measure IEX spreads | Actions | none | nothing |
| 1. Fill-quality logging (expected vs fill price) in the daily executor | `factory/execute.py` | none | nothing |
| 2. #3 Actions executor for 15-minute bars (when repo is public, or accept the minutes) | Actions | #68 | nothing |
| 3. #69 streamer container, local docker-compose, fake websocket and fake broker tests, running the 1-minute tier first | `deploy/streamer/` | #68 | nothing |
| 4. Second-bar data pipeline and event-driven fill model | `factory/` | step 0 | nothing |
| 5. Tier gates and `stream` limits | `protected/` | step 4 | nothing (rule PR with `Reason:`) |
| 6. Deploy to Azure, shadow mode | Azure | step 3 | resource group, storage, second paper key pair, SAS secret |
| 7. Live paper trading of a promoted streaming strategy | Azure | steps 5 and 6 | nothing |

Everything through step 5 needs no Azure account.

## 6. Risks and open questions
- IEX spreads are unmeasured. If they are much wider than SIP spreads, the 5-second tier is dead on
  arrival and the design stops at 1-minute bars.
- Alpaca's paper simulator behaviour (fill prices, partial-fill frequency) should be confirmed
  against Alpaca's current paper-trading docs and against our own fill-quality logs before any model
  depends on it.
- Container Apps scheduled jobs have a maximum run time; confirm it covers a 7-hour session before
  choosing the job over an always-on app.
- Websocket disconnects mid-session are expected. Reconnect, re-reconcile, and treat the gap as stale
  data (no orders) until fresh bars form.
