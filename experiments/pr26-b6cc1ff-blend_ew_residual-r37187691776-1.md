## Experiment `pr26-b6cc1ff-blend_ew_residual-r37187691776-1`: **REJECTED**

Strategy `blend_ew_residual` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "ew_share": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0554 | 0.150993 | 0.142892 | 0.257842 | 2.0964 | 1131 |
| validation | 0.7785 | 0.103662 | 0.139083 | 0.141275 | 2.0181 | 504 |
| holdout | 1.7 |  |  | 0.2 |  |  |

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
| min_trades_validation | pass | 504 |
| max_drawdown_in_sample | **FAIL** | 0.257842 |
| max_vol_in_sample | pass | 0.142892 |
| max_drawdown_validation | pass | 0.141275 |
| max_vol_validation | pass | 0.139083 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.7785 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.277 |
| turnover | pass | 2.0181 |
| robustness | pass | 0.993 |
| fill_participation | pass | 3e-05 |
