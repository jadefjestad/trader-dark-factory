## Experiment `20261004T054839-cross_sectional_momentum`: **REJECTED**

Strategy `cross_sectional_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `fab23ba5f9b8a9a5`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2101 | 0.28503 | 0.229154 | 0.311289 | 5.1264 | 587 |
| validation | 0.9109 | 0.17089 | 0.195479 | 0.163741 | 5.5127 | 240 |
| holdout | 1.3 |  |  | 0.3 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8533
- short_term_reversal: 0.4747

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| min_trades_validation | pass | 240 |
| max_drawdown_in_sample | **FAIL** | 0.311289 |
| max_vol_in_sample | pass | 0.229154 |
| max_drawdown_validation | pass | 0.163741 |
| max_vol_validation | pass | 0.195479 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9109 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.299 |
| turnover | pass | 5.5127 |
| robustness | pass | 0.933 |
| fill_participation | pass | 0.00013 |
