## Experiment `pr57-099edbb-ts_trend_invvol-r37210248410-1`: **PASSED GATES, did not beat champion**

Strategy `ts_trend_invvol` (1Day), params `{"lookback": 252, "skip": 21, "vol_window": 60, "vol_target": 0.1, "rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0691 | 0.132173 | 0.123357 | 0.238776 | 2.6286 | 1302 |
| validation | 0.6928 | 0.069533 | 0.10388 | 0.09867 | 3.042 | 423 |
| holdout | 1.3 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 320-bar reruns matched |
| min_trades_validation | pass | 423 |
| max_drawdown_in_sample | pass | 0.238776 |
| max_vol_in_sample | pass | 0.123357 |
| max_drawdown_validation | pass | 0.09867 |
| max_vol_validation | pass | 0.10388 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6928 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.376 |
| turnover | pass | 3.042 |
| robustness | pass | 0.976 |
| fill_participation | pass | 4e-05 |
