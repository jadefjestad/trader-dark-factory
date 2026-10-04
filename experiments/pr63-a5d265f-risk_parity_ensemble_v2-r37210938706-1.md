## Experiment `pr63-a5d265f-risk_parity_ensemble_v2-r37210938706-1`: **PASSED GATES, did not beat champion**

Strategy `risk_parity_ensemble_v2` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "vol_target": 0.1, "vol_window": 60, "risk_window": 60, "rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0139 | 0.133422 | 0.132156 | 0.249494 | 2.3154 | 1375 |
| validation | 0.7894 | 0.089312 | 0.116725 | 0.10703 | 2.3314 | 525 |
| holdout | 1.6 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 23 experiments, probability the validation Sharpe beats luck is 0.2003 (luck benchmark 1.391 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 700-bar reruns matched |
| min_trades_validation | pass | 525 |
| max_drawdown_in_sample | pass | 0.249494 |
| max_vol_in_sample | pass | 0.132156 |
| max_drawdown_validation | pass | 0.10703 |
| max_vol_validation | pass | 0.116725 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.7894 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.225 |
| turnover | pass | 2.3314 |
| robustness | pass | 0.994 |
| fill_participation | pass | 2e-05 |
