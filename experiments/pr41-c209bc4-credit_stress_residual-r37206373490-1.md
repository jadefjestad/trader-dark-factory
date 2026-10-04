## Experiment `pr41-c209bc4-credit_stress_residual-r37206373490-1`: **PASSED GATES, did not beat champion**

Strategy `credit_stress_residual` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "stress_quantile": 0.8, "stress_exposure": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.3058 | 0.029908 | 0.120417 | 0.244169 | 3.8034 | 483 |
| validation | 0.6914 | 0.062668 | 0.095383 | 0.11056 | 3.6748 | 235 |
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
| min_trades_validation | pass | 235 |
| max_drawdown_in_sample | pass | 0.244169 |
| max_vol_in_sample | pass | 0.120417 |
| max_drawdown_validation | pass | 0.11056 |
| max_vol_validation | pass | 0.095383 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6914 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.386 |
| turnover | pass | 3.6748 |
| robustness | pass | 1.0 |
| fill_participation | pass | 4e-05 |
