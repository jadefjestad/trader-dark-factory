## Experiment `pr87-f091392-gross_profitability_quality-r37242719521-1`: **PASSED GATES, did not beat champion**

Strategy `gross_profitability_quality` (1Day), params `{"top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1406 | 0.144681 | 0.125079 | 0.209647 | 2.0425 | 491 |
| validation | 0.4331 | 0.040582 | 0.102498 | 0.134793 | 0.9489 | 194 |
| holdout | 0.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 24 experiments, probability the validation Sharpe beats luck is 0.0862 (luck benchmark 1.404 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 80-bar reruns matched |
| min_trades_validation | pass | 194 |
| max_drawdown_in_sample | pass | 0.209647 |
| max_vol_in_sample | pass | 0.125079 |
| max_drawdown_validation | pass | 0.134793 |
| max_vol_validation | pass | 0.102498 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.4331 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.708 |
| turnover | pass | 0.9489 |
| robustness | pass | 1.012 |
| fill_participation | pass | 8e-05 |
