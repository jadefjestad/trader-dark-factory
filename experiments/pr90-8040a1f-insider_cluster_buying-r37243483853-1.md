## Experiment `pr90-8040a1f-insider_cluster_buying-r37243483853-1`: **REJECTED**

Strategy `insider_cluster_buying` (1Day), params `{"min_buyers": 1, "slots": 8, "rebalance_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.8623 | 0.117735 | 0.142096 | 0.310854 | 3.3449 | 858 |
| validation | 0.9822 | 0.09599 | 0.098946 | 0.080212 | 3.604 | 335 |
| holdout | 0.3 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 24 experiments, probability the validation Sharpe beats luck is 0.2751 (luck benchmark 1.404 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 30-bar reruns matched |
| min_trades_validation | pass | 335 |
| max_drawdown_in_sample | **FAIL** | 0.310854 |
| max_vol_in_sample | pass | 0.142096 |
| max_drawdown_validation | pass | 0.080212 |
| max_vol_validation | pass | 0.098946 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9822 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.12 |
| turnover | pass | 3.604 |
| robustness | pass | 0.906 |
| fill_participation | pass | 9e-05 |
