## Experiment `pr54-cd073b8-intraday_residual_momentum-r37210152690-1`: **REJECTED**

Strategy `intraday_residual_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.3049 | 0.030285 | 0.123047 | 0.261237 | 3.4881 | 470 |
| validation | 0.486 | 0.047171 | 0.106521 | 0.115384 | 3.0658 | 228 |
| holdout | 0.9 |  |  | 0.2 |  |  |

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
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 228 |
| max_drawdown_in_sample | **FAIL** | 0.261237 |
| max_vol_in_sample | pass | 0.123047 |
| max_drawdown_validation | pass | 0.115384 |
| max_vol_validation | pass | 0.106521 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.486 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.181 |
| turnover | pass | 3.0658 |
| robustness | pass | 1.146 |
| fill_participation | pass | 4e-05 |
