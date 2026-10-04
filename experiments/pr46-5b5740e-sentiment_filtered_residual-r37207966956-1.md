## Experiment `pr46-5b5740e-sentiment_filtered_residual-r37207966956-1`: **PASSED GATES, did not beat champion**

Strategy `sentiment_filtered_residual` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "sentiment_window": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.5528 | 0.062883 | 0.124551 | 0.244169 | 4.3329 | 500 |
| validation | 0.6757 | 0.066632 | 0.104456 | 0.104534 | 5.1649 | 251 |
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
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 251 |
| max_drawdown_in_sample | pass | 0.244169 |
| max_vol_in_sample | pass | 0.124551 |
| max_drawdown_validation | pass | 0.104534 |
| max_vol_validation | pass | 0.104456 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6757 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.123 |
| turnover | pass | 5.1649 |
| robustness | pass | 1.013 |
| fill_participation | pass | 4e-05 |
