## Experiment `pr170-b2d714c-champion_reversal_3day-r38015747358-1`: **PASSED GATES, did not beat champion**

Strategy `champion_reversal_3day` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 3}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9921 | 0.103697 | 0.105087 | 0.185795 | 12.7503 | 5106 |
| validation | 1.0031 | 0.090008 | 0.090333 | 0.06779 | 10.9873 | 2254 |
| holdout | 2.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1734 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 2254 |
| max_drawdown_in_sample | pass | 0.185795 |
| max_vol_in_sample | pass | 0.105087 |
| max_drawdown_validation | pass | 0.06779 |
| max_vol_validation | pass | 0.090333 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0031 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.011 |
| turnover | pass | 10.9873 |
| robustness | pass | 1.001 |
| fill_participation | pass | 3e-05 |
