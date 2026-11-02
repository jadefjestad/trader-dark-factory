## Experiment `pr461-abb3cfb-lcrankwt_pool10vol-r41375753608-1`: **PASSED GATES, did not beat champion**

Strategy `lcrankwt_pool10vol` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-30, fingerprint `0dc99c3b3e413419`, rules `e077534dd4d52fe1`

Beats champion `invvolresid_lcrankwt` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0354 | 0.028652 | 0.027653 | 0.030856 | 3.3925 | 2469 |
| validation | 1.7651 | 0.118143 | 0.064541 | 0.040016 | 3.4113 | 1174 |
| holdout | 2.5 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.5501 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1174 |
| max_drawdown_in_sample | pass | 0.030856 |
| max_vol_in_sample | pass | 0.027653 |
| max_drawdown_validation | pass | 0.040016 |
| max_vol_validation | pass | 0.064541 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.7651 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.73 |
| turnover | pass | 3.4113 |
| robustness | pass | 1.001 |
| fill_participation | pass | 3e-05 |
