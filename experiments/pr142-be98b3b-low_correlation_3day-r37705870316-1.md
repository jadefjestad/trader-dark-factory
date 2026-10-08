## Experiment `pr142-be98b3b-low_correlation_3day-r37705870316-1`: **PASSED GATES, did not beat champion**

Strategy `low_correlation_3day` (1Day), params `{"corr_window": 504, "horizon": 3, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `cc4377c250a631b2`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.7796 | 0.081607 | 0.108243 | 0.19907 | 1.7869 | 407 |
| validation | 0.7806 | 0.07587 | 0.097215 | 0.072618 | 1.5321 | 196 |
| holdout | 1.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 53 experiments, probability the validation Sharpe beats luck is 0.1167 (luck benchmark 1.63 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 196 |
| max_drawdown_in_sample | pass | 0.19907 |
| max_vol_in_sample | pass | 0.108243 |
| max_drawdown_validation | pass | 0.072618 |
| max_vol_validation | pass | 0.097215 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.7806 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.001 |
| turnover | pass | 1.5321 |
| robustness | pass | 1.042 |
| fill_participation | pass | 4e-05 |
