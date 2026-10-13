## Experiment `pr209-877be53-downside_severe_reveach21-r38354675877-1`: **PASSED GATES, did not beat champion**

Strategy `downside_severe_reveach21` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-12, fingerprint `709958ffc91b07e6`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1289 | 0.102512 | 0.090098 | 0.132466 | 5.9073 | 1130 |
| validation | 1.2489 | 0.124313 | 0.098297 | 0.080998 | 5.7302 | 503 |
| holdout | 2.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2762 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 503 |
| max_drawdown_in_sample | pass | 0.132466 |
| max_vol_in_sample | pass | 0.090098 |
| max_drawdown_validation | pass | 0.080998 |
| max_vol_validation | pass | 0.098297 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.2489 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.12 |
| turnover | pass | 5.7302 |
| robustness | pass | 0.982 |
| fill_participation | pass | 3e-05 |
