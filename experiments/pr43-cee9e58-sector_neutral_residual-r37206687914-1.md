## Experiment `pr43-cee9e58-sector_neutral_residual-r37206687914-1`: **REJECTED**

Strategy `sector_neutral_residual` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.3585 | 0.037317 | 0.123861 | 0.261119 | 3.2233 | 456 |
| validation | 0.5771 | 0.05537 | 0.103851 | 0.158838 | 3.2533 | 234 |
| holdout | 1.8 |  |  | 0.1 |  |  |

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
| min_trades_validation | pass | 234 |
| max_drawdown_in_sample | **FAIL** | 0.261119 |
| max_vol_in_sample | pass | 0.123861 |
| max_drawdown_validation | pass | 0.158838 |
| max_vol_validation | pass | 0.103851 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.5771 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.219 |
| turnover | pass | 3.2533 |
| robustness | pass | 1.028 |
| fill_participation | pass | 4e-05 |
