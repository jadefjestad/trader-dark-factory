## Experiment `pr161-b7df9d5-ltr_sleeve_biweekly-r37915415626-1`: **PASSED GATES, did not beat champion**

Strategy `ltr_sleeve_biweekly` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 10, "ltr_formation": 756, "ltr_skip": 252}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `1f6e9538633368a7`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.8359 | 0.082526 | 0.101064 | 0.224979 | 6.1995 | 2687 |
| validation | 1.3 | 0.119452 | 0.089864 | 0.068287 | 5.7296 | 1181 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.301 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 800-bar reruns matched |
| min_trades_validation | pass | 1181 |
| max_drawdown_in_sample | pass | 0.224979 |
| max_vol_in_sample | pass | 0.101064 |
| max_drawdown_validation | pass | 0.068287 |
| max_vol_validation | pass | 0.089864 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.3 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.464 |
| turnover | pass | 5.7296 |
| robustness | pass | 1.002 |
| fill_participation | pass | 3e-05 |
