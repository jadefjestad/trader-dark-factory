## Experiment `pr55-e98c1d8-news_shock_drift-r37210185459-1`: **REJECTED**

Strategy `news_shock_drift` (1Day), params `{"base_window": 60, "spike": 3.0, "min_articles": 3, "hold": 10, "slots": 8}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.6894 | 0.087493 | 0.132225 | 0.215894 | 35.7456 | 6530 |
| validation | 0.59 | 0.071245 | 0.12994 | 0.145315 | 34.9864 | 2644 |
| holdout | 1.6 |  |  | 0.1 |  |  |

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
| lookback_sufficient | pass | 5 90-bar reruns matched |
| min_trades_validation | pass | 2644 |
| max_drawdown_in_sample | pass | 0.215894 |
| max_vol_in_sample | pass | 0.132225 |
| max_drawdown_validation | pass | 0.145315 |
| max_vol_validation | pass | 0.12994 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.59 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.099 |
| turnover | **FAIL** | 34.9864 |
| robustness | pass | 1.091 |
| fill_participation | pass | 0.00018 |
