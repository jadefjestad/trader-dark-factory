## Experiment `pr136-77d66d3-residual_reversal-r37633837811-1`: **PASSED GATES, did not beat champion**

Strategy `residual_reversal` (1Day), params `{"beta_window": 252, "window": 21, "top_n": 8, "rebalance_every": 5, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `345cc0efb7fadc81`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_blend` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2384 | 0.135587 | 0.107367 | 0.161111 | 23.9119 | 2582 |
| validation | 0.7123 | 0.068041 | 0.101427 | 0.10259 | 21.7622 | 1081 |
| holdout | 1.9 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 48 experiments, probability the validation Sharpe beats luck is 0.1049 (luck benchmark 1.603 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 340-bar reruns matched |
| min_trades_validation | pass | 1081 |
| max_drawdown_in_sample | pass | 0.161111 |
| max_vol_in_sample | pass | 0.107367 |
| max_drawdown_validation | pass | 0.10259 |
| max_vol_validation | pass | 0.101427 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.7123 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.526 |
| turnover | pass | 21.7622 |
| robustness | pass | 0.99 |
| fill_participation | pass | 0.00014 |
