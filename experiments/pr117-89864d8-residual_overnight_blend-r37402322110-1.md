## Experiment `pr117-89864d8-residual_overnight_blend-r37402322110-1`: **PASSED GATES, did not beat champion**

Strategy `residual_overnight_blend` (1Day), params `{"lookback": 252, "skip": 21, "window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "overnight_share": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-05, fingerprint `09d3c531a4e21501`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.6882 | 0.079296 | 0.121802 | 0.228606 | 3.2253 | 776 |
| validation | 0.8948 | 0.087 | 0.099318 | 0.085597 | 3.089 | 328 |
| holdout | 1.5 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 30 experiments, probability the validation Sharpe beats luck is 0.2098 (luck benchmark 1.47 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 328 |
| max_drawdown_in_sample | pass | 0.228606 |
| max_vol_in_sample | pass | 0.121802 |
| max_drawdown_validation | pass | 0.085597 |
| max_vol_validation | pass | 0.099318 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8948 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.207 |
| turnover | pass | 3.089 |
| robustness | pass | 0.996 |
| fill_participation | pass | 3e-05 |
