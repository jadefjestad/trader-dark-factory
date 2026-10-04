## Experiment `pr13-efba455-breadth_regime_equal_weight-r37182424674-1`: **REJECTED**

Strategy `breadth_regime_equal_weight` (1Day), params `{"rebalance_every": 21, "trend": 200, "breadth": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2665 | 0.201184 | 0.153945 | 0.279599 | 3.6337 | 1500 |
| validation | 0.2632 | 0.027161 | 0.132465 | 0.213932 | 9.4725 | 817 |
| holdout | 1.7 |  |  | 0.1 |  |  |

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
| min_trades_validation | pass | 817 |
| max_drawdown_in_sample | **FAIL** | 0.279599 |
| max_vol_in_sample | pass | 0.153945 |
| max_drawdown_validation | pass | 0.213932 |
| max_vol_validation | pass | 0.132465 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | 0.2632 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | **FAIL** | 1.003 |
| turnover | pass | 9.4725 |
| robustness | pass | 1.311 |
| fill_participation | pass | 0.00011 |
