## Experiment `pr42-0e4f17e-invvol_reversal-r37206547527-1`: **REJECTED**

Strategy `invvol_reversal` (1Day), params `{"window": 5, "bottom_n": 8, "trend": 200, "rebalance_every": 5, "vol_window": 20}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1966 | 0.20678 | 0.168777 | 0.234004 | 60.775 | 3263 |
| validation | 0.2445 | 0.027241 | 0.153581 | 0.18244 | 44.9191 | 1150 |
| holdout | 0.5 |  |  | 0.3 |  |  |

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
| lookback_sufficient | pass | 5 210-bar reruns matched |
| min_trades_validation | pass | 1150 |
| max_drawdown_in_sample | pass | 0.234004 |
| max_vol_in_sample | pass | 0.168777 |
| max_drawdown_validation | pass | 0.18244 |
| max_vol_validation | pass | 0.153581 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | 0.2445 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.952 |
| turnover | **FAIL** | 44.9191 |
| robustness | pass | 1.121 |
| fill_participation | pass | 0.00039 |
