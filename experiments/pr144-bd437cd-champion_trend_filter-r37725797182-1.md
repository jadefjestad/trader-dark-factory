## Experiment `pr144-bd437cd-champion_trend_filter-r37725797182-1`: **PASSED GATES, did not beat champion**

Strategy `champion_trend_filter` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5, "trend_window": 200, "bear_scale": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `cc4377c250a631b2`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9859 | 0.102652 | 0.104743 | 0.188712 | 10.1633 | 3951 |
| validation | 0.9886 | 0.077226 | 0.078991 | 0.072256 | 9.0658 | 1648 |
| holdout | 2.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 55 experiments, probability the validation Sharpe beats luck is 0.1828 (luck benchmark 1.64 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 1648 |
| max_drawdown_in_sample | pass | 0.188712 |
| max_vol_in_sample | pass | 0.104743 |
| max_drawdown_validation | pass | 0.072256 |
| max_vol_validation | pass | 0.078991 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9886 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.003 |
| turnover | pass | 9.0658 |
| robustness | pass | 0.999 |
| fill_participation | pass | 4e-05 |
