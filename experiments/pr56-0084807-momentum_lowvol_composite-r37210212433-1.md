## Experiment `pr56-0084807-momentum_lowvol_composite-r37210212433-1`: **REJECTED**

Strategy `momentum_lowvol_composite` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.6237 | 0.0708 | 0.121697 | 0.222849 | 4.921 | 486 |
| validation | 0.6439 | 0.064339 | 0.105254 | 0.08458 | 4.4828 | 228 |
| holdout | 1.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | **FAIL** | gross exposure 1.125 > 1.0 |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 228 |
| max_drawdown_in_sample | pass | 0.222849 |
| max_vol_in_sample | pass | 0.121697 |
| max_drawdown_validation | pass | 0.08458 |
| max_vol_validation | pass | 0.105254 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6439 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.02 |
| turnover | pass | 4.4828 |
| robustness | pass | 0.977 |
| fill_participation | pass | 4e-05 |
