## Experiment `pr160-3aea7cd-champion_ltr_sleeve-r37902738976-1`: **PASSED GATES, did not beat champion**

Strategy `champion_ltr_sleeve` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5, "ltr_formation": 756, "ltr_skip": 252}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `1f6e9538633368a7`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.8716 | 0.085551 | 0.1 | 0.214743 | 7.9674 | 3910 |
| validation | 1.2519 | 0.113442 | 0.089292 | 0.069822 | 7.3173 | 1756 |
| holdout | 1.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.278 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 800-bar reruns matched |
| min_trades_validation | pass | 1756 |
| max_drawdown_in_sample | pass | 0.214743 |
| max_vol_in_sample | pass | 0.1 |
| max_drawdown_validation | pass | 0.069822 |
| max_vol_validation | pass | 0.089292 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.2519 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.38 |
| turnover | pass | 7.3173 |
| robustness | pass | 1.0 |
| fill_participation | pass | 3e-05 |
