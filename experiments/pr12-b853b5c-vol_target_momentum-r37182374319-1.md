## Experiment `pr12-b853b5c-vol_target_momentum-r37182374319-1`: **REJECTED**

Strategy `vol_target_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.12, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0139 | 0.149588 | 0.148488 | 0.251654 | 4.1337 | 572 |
| validation | 0.9428 | 0.117214 | 0.126894 | 0.094563 | 4.3608 | 236 |
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
| min_trades_validation | pass | 236 |
| max_drawdown_in_sample | **FAIL** | 0.251654 |
| max_vol_in_sample | pass | 0.148488 |
| max_drawdown_validation | pass | 0.094563 |
| max_vol_validation | pass | 0.126894 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9428 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.071 |
| turnover | pass | 4.3608 |
| robustness | pass | 0.996 |
| fill_participation | pass | 6e-05 |
