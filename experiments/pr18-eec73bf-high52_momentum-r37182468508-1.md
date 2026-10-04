## Experiment `pr18-eec73bf-high52_momentum-r37182468508-1`: **REJECTED**

Strategy `high52_momentum` (1Day), params `{"window": 252, "top_n": 8, "rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1881 | 0.227185 | 0.187229 | 0.303638 | 11.285 | 687 |
| validation | 0.4041 | 0.051947 | 0.148174 | 0.180295 | 8.065 | 247 |
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
| min_trades_validation | pass | 247 |
| max_drawdown_in_sample | **FAIL** | 0.303638 |
| max_vol_in_sample | pass | 0.187229 |
| max_drawdown_validation | pass | 0.180295 |
| max_vol_validation | pass | 0.148174 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.4041 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.784 |
| turnover | pass | 8.065 |
| robustness | pass | 1.311 |
| fill_participation | pass | 9e-05 |
