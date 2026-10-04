## Experiment `pr44-a0a2c22-news_confirmed_residual_momentum-r37207275898-1`: **PASSED GATES, did not beat champion**

Strategy `news_confirmed_residual_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "news_window": 63, "min_attention": 1.0}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.5559 | 0.061883 | 0.121403 | 0.219872 | 4.9228 | 510 |
| validation | 0.6005 | 0.060132 | 0.104563 | 0.116122 | 4.2441 | 233 |
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
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 233 |
| max_drawdown_in_sample | pass | 0.219872 |
| max_vol_in_sample | pass | 0.121403 |
| max_drawdown_validation | pass | 0.116122 |
| max_vol_validation | pass | 0.104563 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6005 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.045 |
| turnover | pass | 4.2441 |
| robustness | pass | 1.009 |
| fill_participation | pass | 4e-05 |
