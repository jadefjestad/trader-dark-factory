## Experiment `pr139-943105a-champion_earnings_sleeve-r37679382417-1`: **PASSED GATES, did not beat champion**

Strategy `champion_earnings_sleeve` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5, "window_start": 45, "window_end": 70}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `40e75477f858e950`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1627 | 0.114854 | 0.097897 | 0.161983 | 11.0787 | 4692 |
| validation | 1.0876 | 0.095869 | 0.088014 | 0.076826 | 10.0583 | 1949 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 51 experiments, probability the validation Sharpe beats luck is 0.2286 (luck benchmark 1.62 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 1949 |
| max_drawdown_in_sample | pass | 0.161983 |
| max_vol_in_sample | pass | 0.097897 |
| max_drawdown_validation | pass | 0.076826 |
| max_vol_validation | pass | 0.088014 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0876 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.075 |
| turnover | pass | 10.0583 |
| robustness | pass | 1.012 |
| fill_participation | pass | 3e-05 |
