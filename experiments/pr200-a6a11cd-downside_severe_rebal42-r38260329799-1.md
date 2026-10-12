## Experiment `pr200-a6a11cd-downside_severe_rebal42-r38260329799-1`: **PASSED GATES, did not beat champion**

Strategy `downside_severe_rebal42` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 42, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-12, fingerprint `831532f3613657c1`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1755 | 0.105246 | 0.088588 | 0.109395 | 10.2732 | 3435 |
| validation | 1.0485 | 0.100914 | 0.097298 | 0.081634 | 9.652 | 1612 |
| holdout | 2.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1913 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1612 |
| max_drawdown_in_sample | pass | 0.109395 |
| max_vol_in_sample | pass | 0.088588 |
| max_drawdown_validation | pass | 0.081634 |
| max_vol_validation | pass | 0.097298 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0485 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.127 |
| turnover | pass | 9.652 |
| robustness | pass | 1.022 |
| fill_participation | pass | 4e-05 |
