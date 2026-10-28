## Experiment `pr406-38079c6-gpfilter_corr_minsixth-r40741930360-1`: **PASSED GATES, did not beat champion**

Strategy `gpfilter_corr_minsixth` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-28, fingerprint `ed0d436778c9f087`, rules `e077534dd4d52fe1`

Beats champion `gpfilter_wts_10_80_10` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0124 | 0.089578 | 0.088858 | 0.181019 | 4.2737 | 3101 |
| validation | 1.3838 | 0.159596 | 0.111863 | 0.095854 | 4.5073 | 1488 |
| holdout | 2.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.3429 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1488 |
| max_drawdown_in_sample | pass | 0.181019 |
| max_vol_in_sample | pass | 0.088858 |
| max_drawdown_validation | pass | 0.095854 |
| max_vol_validation | pass | 0.111863 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.3838 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.371 |
| turnover | pass | 4.5073 |
| robustness | pass | 0.988 |
| fill_participation | pass | 6e-05 |
