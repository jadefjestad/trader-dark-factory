## Experiment `pr460-1cbd60f-lcrankwt_portvt-r41365256840-1`: **PASSED GATES, did not beat champion**

Strategy `lcrankwt_portvt` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-30, fingerprint `0dc99c3b3e413419`, rules `e077534dd4d52fe1`

Beats champion `invvolresid_lcrankwt` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0382 | 0.028057 | 0.027004 | 0.030856 | 3.3655 | 2462 |
| validation | 2.2328 | 0.144461 | 0.061357 | 0.038793 | 3.6785 | 1224 |
| holdout | 2.6 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.7851 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1224 |
| max_drawdown_in_sample | pass | 0.030856 |
| max_vol_in_sample | pass | 0.027004 |
| max_drawdown_validation | pass | 0.038793 |
| max_vol_validation | pass | 0.061357 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 2.2328 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -1.195 |
| turnover | pass | 3.6785 |
| robustness | pass | 0.989 |
| fill_participation | pass | 3e-05 |
