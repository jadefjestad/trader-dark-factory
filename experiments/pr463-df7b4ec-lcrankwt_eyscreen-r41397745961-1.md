## Experiment `pr463-df7b4ec-lcrankwt_eyscreen-r41397745961-1`: **PASSED GATES, did not beat champion**

Strategy `lcrankwt_eyscreen` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-30, fingerprint `0dc99c3b3e413419`, rules `e077534dd4d52fe1`

Beats champion `invvolresid_lcrankwt` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9576 | 0.027566 | 0.028833 | 0.030856 | 3.4024 | 2463 |
| validation | 1.6846 | 0.110607 | 0.063574 | 0.044098 | 3.5414 | 1189 |
| holdout | 2.3 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.5038 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1189 |
| max_drawdown_in_sample | pass | 0.030856 |
| max_vol_in_sample | pass | 0.028833 |
| max_drawdown_validation | pass | 0.044098 |
| max_vol_validation | pass | 0.063574 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.6846 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.727 |
| turnover | pass | 3.5414 |
| robustness | pass | 1.0 |
| fill_participation | pass | 3e-05 |
