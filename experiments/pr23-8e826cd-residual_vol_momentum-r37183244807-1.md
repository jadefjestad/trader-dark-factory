## Experiment `pr23-8e826cd-residual_vol_momentum-r37183244807-1`: **PROMOTE**

Strategy `residual_vol_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `blend_ew_vol_momentum` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.4066 | 0.043728 | 0.124597 | 0.244169 | 3.823 | 486 |
| validation | 0.8768 | 0.090891 | 0.106383 | 0.084366 | 3.4933 | 233 |
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
| min_trades_validation | pass | 233 |
| max_drawdown_in_sample | pass | 0.244169 |
| max_vol_in_sample | pass | 0.124597 |
| max_drawdown_validation | pass | 0.084366 |
| max_vol_validation | pass | 0.106383 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8768 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.47 |
| turnover | pass | 3.4933 |
| robustness | pass | 1.0 |
| fill_participation | pass | 4e-05 |
