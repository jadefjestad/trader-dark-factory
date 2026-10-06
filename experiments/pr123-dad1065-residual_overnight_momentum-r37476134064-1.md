## Experiment `pr123-dad1065-residual_overnight_momentum-r37476134064-1`: **PASSED GATES, did not beat champion**

Strategy `residual_overnight_momentum` (1Day), params `{"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `b12d607b2ead8042`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.5853 | 0.062145 | 0.114285 | 0.194638 | 2.6592 | 451 |
| validation | 0.5773 | 0.05493 | 0.101148 | 0.127694 | 2.8964 | 222 |
| holdout | 1.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 36 experiments, probability the validation Sharpe beats luck is 0.0916 (luck benchmark 1.523 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 222 |
| max_drawdown_in_sample | pass | 0.194638 |
| max_vol_in_sample | pass | 0.114285 |
| max_drawdown_validation | pass | 0.127694 |
| max_vol_validation | pass | 0.101148 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.5773 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.008 |
| turnover | pass | 2.8964 |
| robustness | pass | 1.002 |
| fill_participation | pass | 4e-05 |
