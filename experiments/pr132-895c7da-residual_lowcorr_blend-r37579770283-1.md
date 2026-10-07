## Experiment `pr132-895c7da-residual_lowcorr_blend-r37579770283-1`: **PROMOTE**

Strategy `residual_lowcorr_blend` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "low_corr_share": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `a02241d089b64dc6`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.854 | 0.093614 | 0.112276 | 0.207033 | 2.9441 | 813 |
| validation | 1.0829 | 0.100529 | 0.092637 | 0.068451 | 2.3464 | 324 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 44 experiments, probability the validation Sharpe beats luck is 0.2446 (luck benchmark 1.579 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 324 |
| max_drawdown_in_sample | pass | 0.207033 |
| max_vol_in_sample | pass | 0.112276 |
| max_drawdown_validation | pass | 0.068451 |
| max_vol_validation | pass | 0.092637 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0829 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.229 |
| turnover | pass | 2.3464 |
| robustness | pass | 1.0 |
| fill_participation | pass | 3e-05 |
