## Experiment `pr131-a66a74b-low_correlation-r37569662792-1`: **PASSED GATES, did not beat champion**

Strategy `low_correlation` (1Day), params `{"corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `a02241d089b64dc6`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2157 | 0.143235 | 0.115698 | 0.177427 | 2.3982 | 509 |
| validation | 1.1215 | 0.108213 | 0.095561 | 0.073513 | 1.3481 | 198 |
| holdout | 0.9 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 43 experiments, probability the validation Sharpe beats luck is 0.2635 (luck benchmark 1.573 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 300-bar reruns matched |
| min_trades_validation | pass | 198 |
| max_drawdown_in_sample | pass | 0.177427 |
| max_vol_in_sample | pass | 0.115698 |
| max_drawdown_validation | pass | 0.073513 |
| max_vol_validation | pass | 0.095561 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.1215 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.094 |
| turnover | pass | 1.3481 |
| robustness | pass | 1.008 |
| fill_participation | pass | 6e-05 |
