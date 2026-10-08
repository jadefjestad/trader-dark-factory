## Experiment `pr152-ab372ed-champion_turn_of_month-r37821613530-1`: **REJECTED**

Strategy `champion_turn_of_month` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5, "tom_start_day": 26, "tom_end_day": 4, "off_scale": 0.6}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `c705eabcf9f3b3d5`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9289 | 0.074379 | 0.080777 | 0.122043 | 12.3977 | 4873 |
| validation | 1.0442 | 0.068939 | 0.066515 | 0.050993 | 11.5685 | 2050 |
| holdout | 1.6 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 62 experiments, probability the validation Sharpe beats luck is 0.1889 (luck benchmark 1.672 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | **FAIL** | with only 520 bars (as live) signals differ at ['2023-10-30 00:00:00'] |
| min_trades_validation | pass | 2050 |
| max_drawdown_in_sample | pass | 0.122043 |
| max_vol_in_sample | pass | 0.080777 |
| max_drawdown_validation | pass | 0.050993 |
| max_vol_validation | pass | 0.066515 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0442 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.115 |
| turnover | pass | 11.5685 |
| robustness | pass | 1.0 |
| fill_participation | pass | 6e-05 |
