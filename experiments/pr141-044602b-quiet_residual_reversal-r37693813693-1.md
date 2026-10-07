## Experiment `pr141-044602b-quiet_residual_reversal-r37693813693-1`: **PASSED GATES, did not beat champion**

Strategy `quiet_residual_reversal` (1Day), params `{"beta_window": 252, "window": 21, "top_n": 8, "screen_n": 16, "volume_window": 21, "rebalance_every": 5, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `cc4377c250a631b2`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9797 | 0.105071 | 0.107991 | 0.173671 | 23.1358 | 2500 |
| validation | 0.319 | 0.027591 | 0.104849 | 0.117586 | 21.5272 | 1073 |
| holdout | 1.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 52 experiments, probability the validation Sharpe beats luck is 0.0333 (luck benchmark 1.625 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 340-bar reruns matched |
| min_trades_validation | pass | 1073 |
| max_drawdown_in_sample | pass | 0.173671 |
| max_vol_in_sample | pass | 0.107991 |
| max_drawdown_validation | pass | 0.117586 |
| max_vol_validation | pass | 0.104849 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.319 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.661 |
| turnover | pass | 21.5272 |
| robustness | pass | 0.942 |
| fill_participation | pass | 0.00013 |
