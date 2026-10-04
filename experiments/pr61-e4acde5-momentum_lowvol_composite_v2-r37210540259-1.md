## Experiment `pr61-e4acde5-momentum_lowvol_composite_v2-r37210540259-1`: **PASSED GATES, did not beat champion**

Strategy `momentum_lowvol_composite_v2` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.638 | 0.073158 | 0.122599 | 0.222868 | 4.7708 | 486 |
| validation | 0.745 | 0.07596 | 0.105608 | 0.088671 | 4.5142 | 233 |
| holdout | 1.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 21 experiments, probability the validation Sharpe beats luck is 0.1946 (luck benchmark 1.363 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 233 |
| max_drawdown_in_sample | pass | 0.222868 |
| max_vol_in_sample | pass | 0.122599 |
| max_drawdown_validation | pass | 0.088671 |
| max_vol_validation | pass | 0.105608 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.745 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.107 |
| turnover | pass | 4.5142 |
| robustness | pass | 0.908 |
| fill_participation | pass | 4e-05 |
