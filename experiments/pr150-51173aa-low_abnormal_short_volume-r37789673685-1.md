## Experiment `pr150-51173aa-low_abnormal_short_volume-r37789673685-1`: **PASSED GATES, did not beat champion**

Strategy `low_abnormal_short_volume` (1Day), params `{"short_window": 21, "long_window": 126, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `dd9c07c024142861`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.5303 | 0.050442 | 0.102947 | 0.242258 | 4.3761 | 382 |
| validation | 0.3202 | 0.029433 | 0.105224 | 0.15027 | 8.754 | 305 |
| holdout | 1.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 60 experiments, probability the validation Sharpe beats luck is 0.0295 (luck benchmark 1.663 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 200-bar reruns matched |
| min_trades_validation | pass | 305 |
| max_drawdown_in_sample | pass | 0.242258 |
| max_vol_in_sample | pass | 0.102947 |
| max_drawdown_validation | pass | 0.15027 |
| max_vol_validation | pass | 0.105224 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.3202 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.21 |
| turnover | pass | 8.754 |
| robustness | pass | 1.088 |
| fill_participation | pass | 4e-05 |
