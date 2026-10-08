## Experiment `pr148-e9b4430-low_abnormal_volume-r37761122236-1`: **PASSED GATES, did not beat champion**

Strategy `low_abnormal_volume` (1Day), params `{"short_window": 21, "long_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `cc4377c250a631b2`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0127 | 0.119914 | 0.118899 | 0.231731 | 9.779 | 735 |
| validation | 0.3599 | 0.032665 | 0.103106 | 0.120278 | 7.8553 | 283 |
| holdout | 0.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 58 experiments, probability the validation Sharpe beats luck is 0.0348 (luck benchmark 1.654 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 300-bar reruns matched |
| min_trades_validation | pass | 283 |
| max_drawdown_in_sample | pass | 0.231731 |
| max_vol_in_sample | pass | 0.118899 |
| max_drawdown_validation | pass | 0.120278 |
| max_vol_validation | pass | 0.103106 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.3599 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.653 |
| turnover | pass | 7.8553 |
| robustness | pass | 1.308 |
| fill_participation | pass | 8e-05 |
