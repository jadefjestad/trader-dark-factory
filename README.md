# Trader Dark Factory

An autonomous, cloud-hosted **paper-trading** research factory. A Claude Routine proposes one strategy
change at a time; deterministic Python backtests it against fixed rules; GitHub PRs carry the
results; a verified winner is promoted by merging; GitHub Actions trades the promoted strategy on an
Alpaca paper account every weekday, with or without Claude.

```
Claude Routine (research, budgeted)         GitHub Actions (deterministic, no Claude needed)
───────────────────────────────────         ────────────────────────────────────────────────
reads ledger + backlog issues        ──►    evaluate.yml  on every PR
writes ONE candidate strategy               ├─ data job: downloads Alpaca bars (has keys, runs base code only)
opens experiment PR                         ├─ evaluate job: runs candidate as an unprivileged user, NO secrets
                                            └─ report job: gates verdict, PR comment, ledger branch
copies champion.json if PROMOTE      ──►    merge = promotion (state/champion.json on main)
                                            execute.yml  weekdays: champion → Alpaca PAPER orders
                                            ci.yml       tests + guard on every PR
```

## Rules, limits and hard invariants
The agent manages everything itself, including the rule files (Jade, 2026-10-04):
| Path | Holds |
|---|---|
| `protected/evaluation.yaml` | periods (in-sample / validation / unseen holdout), costs, slippage, gates, promotion rule |
| `protected/risk_limits.yaml` | kill switch, exposure and order limits, drawdown halt, data staleness |
| `protected/universe.yaml` | tradable symbols and the SPY benchmark |

A few things are hard invariants that no rule file can change. They live in `factory/invariants.py`,
are tested by `tests/test_invariants.py`, and agent branches may not edit either file:
- **Paper only.** The only broker endpoint is the paper one; the live endpoint may appear nowhere;
  `paper_only` must be true and the account number must start with `PA`.
- **Fail closed.** No orders when data, authentication or validation fails.
- **Failed experiments are kept.** Candidate files on main are immutable; the ledger is append-only.
- **Rule changes are logged.** A PR touching rules or limits needs a `Reason:` line, and on merge CI
  writes a `rules/` record to the ledger with every changed value (before and after) and the reason.

Strategy code never runs inside the evaluator or executor: `factory/runner.py` runs it in a child
process with a private copy of code and data, an empty environment, a timeout and (in Actions) a
separate unprivileged OS user, and reads back only numeric weights. `evaluate.yml` runs the evaluator
and rules from the base branch, never the PR's copy, so a rule change only applies once merged.

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
  holdout Sharpe) by 0.05, re-run on identical data. The score itself is never published, since it
  would reveal the holdout Sharpe. Synthetic data and timeframes without an executor are never promotable.

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
