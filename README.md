# Trader Dark Factory

An autonomous, cloud-hosted **paper-trading** research factory. A Claude Routine proposes one strategy
change at a time; deterministic Python backtests it against protected rules; GitHub PRs carry the
results; a verified winner is promoted by merging; GitHub Actions trades the promoted strategy on an
Alpaca paper account every weekday, with or without Claude.

```
Claude Routine (research, budgeted)         GitHub Actions (deterministic, no Claude needed)
───────────────────────────────────         ────────────────────────────────────────────────
reads ledger + backlog issues        ──►    evaluate.yml  on every PR
writes ONE candidate strategy               ├─ data job: downloads Alpaca bars (has keys, runs base code only)
opens experiment PR                         ├─ evaluate job: runs candidate, NO secrets, read-only
                                            └─ report job: gates verdict, PR comment, ledger branch
copies champion.json if PROMOTE      ──►    merge = promotion (state/champion.json on main)
                                            execute.yml  weekdays: champion → Alpaca PAPER orders
                                            ci.yml       tests + guard on every PR
```

## What is protected from the agent
| Path | Holds |
|---|---|
| `protected/evaluation.yaml` | periods (in-sample / validation / unseen holdout), costs, slippage, gates, promotion rule |
| `protected/risk_limits.yaml` | kill switch, exposure and order limits, drawdown halt, data staleness |
| `protected/universe.yaml` | tradable symbols and the SPY benchmark |
| `factory/`, `strategies/baselines/`, `strategies/base.py`, `scripts/`, `.github/` | the evaluator, executor, baselines and workflows |

Enforced three ways: CODEOWNERS (Jade's review), `scripts/guard.py` in CI (agent branches may not touch
these paths at all), and `evaluate.yml` running the evaluator from the base branch, never the PR's copy.

## How a candidate is judged
- Signals use bar t's close, fills happen at bar t+1's open, plus slippage, half-spread and sell fees.
- Intraday strategies are forced flat at each session close.
- **No look-ahead**: the strategy is rerun on truncated data at several random cut points; any
  difference from the full run fails the `no_lookahead` gate.
- **Overfitting**: in-sample vs validation Sharpe decay, ±20% parameter-perturbation robustness,
  minimum trade count, and a holdout period reported only coarsely so the agent cannot tune to it.
- **Risk**: drawdown, volatility, turnover, position-size and gross-exposure gates; order size vs bar
  dollar volume.
- **Promotion**: pass every gate AND beat the current champion's score (mean of validation and
  holdout Sharpe) by 0.05, re-run on identical data. Synthetic data is never promotable.

Every result, pass or fail, is appended to the `ledger` branch (`experiments/`), and every execution
run to `ledger/executions/`. Candidate files are never deleted.

## Fail-closed execution
`factory/execute.py` places no orders if: keys are missing, the account isn't an `PA…` paper account,
the kill switch is off, drawdown exceeds the halt, open orders already exist, data is stale or missing a
symbol, weights break a risk limit, or anything raises. The broker client only knows the paper endpoint.

## Daily vs intraday vs "high frequency" on the free Alpaca plan
- **Daily**: fully supported end to end (backtest, evaluation, promotion, execution).
- **Intraday (15-minute bars)**: supported in backtests and evaluation using historical SIP bars. There is
  no intraday executor yet; it is the first feature in the factory's own backlog.
- **High frequency**: not realistic here. The free plan streams real-time data from IEX only (a few
  percent of volume, 30 symbols), REST is limited to 200 requests/minute, paper fills are simulated,
  and GitHub cron runs at best every 5 minutes with delays. The realistic floor is minute-bar strategies
  with decisions every 1 to 5 minutes from a long-running Actions job (max 6 hours per job).

## Claude usage budgeting (honest version)
Claude does not expose remaining subscription usage to a Routine, and there is no API for it. The
factory therefore budgets itself: each Routine run logs `start` and `end` events as comments on the
"Factory usage log" issue (`factory/usage.py`). A run that starts but never ends is treated as having
hit a usage limit; the next runs cool down for one 5-hour window and shrink their batch. Runs that
finish their whole batch grow the next batch, up to the cap in `agent/usage_policy.yaml`. Work is
queued as `backlog` issues so every run that is allowed has something useful to do. Execution never
depends on Claude.

See [docs/SETUP.md](docs/SETUP.md) for the one-time manual steps.
