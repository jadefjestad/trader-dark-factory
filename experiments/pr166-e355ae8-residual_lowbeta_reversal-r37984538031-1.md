## Experiment `pr166-e355ae8-residual_lowbeta_reversal-r37984538031-1`: **PASSED GATES, did not beat champion**

Strategy `residual_lowbeta_reversal` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `7ca59406bd2bdf24`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0416 | 0.106519 | 0.102257 | 0.186069 | 10.0922 | 3912 |
| validation | 0.9871 | 0.087852 | 0.089648 | 0.071255 | 8.949 | 1700 |
| holdout | 2.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1682 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1700 |
| max_drawdown_in_sample | pass | 0.186069 |
| max_vol_in_sample | pass | 0.102257 |
| max_drawdown_validation | pass | 0.071255 |
| max_vol_validation | pass | 0.089648 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9871 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.055 |
| turnover | pass | 8.949 |
| robustness | pass | 0.985 |
| fill_participation | pass | 4e-05 |
