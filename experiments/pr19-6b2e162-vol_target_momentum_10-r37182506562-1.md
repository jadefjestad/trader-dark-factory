## Experiment `pr19-6b2e162-vol_target_momentum_10-r37182506562-1`: **PASSED GATES, did not beat champion**

Strategy `vol_target_momentum_10` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0223 | 0.12686 | 0.124481 | 0.21005 | 3.5735 | 569 |
| validation | 0.9422 | 0.097981 | 0.105804 | 0.07892 | 3.6377 | 234 |
| holdout | 1.3 |  |  | 0.1 |  |  |

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
| min_trades_validation | pass | 234 |
| max_drawdown_in_sample | pass | 0.21005 |
| max_vol_in_sample | pass | 0.124481 |
| max_drawdown_validation | pass | 0.07892 |
| max_vol_validation | pass | 0.105804 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9422 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.08 |
| turnover | pass | 3.6377 |
| robustness | pass | 1.0 |
| fill_participation | pass | 5e-05 |
