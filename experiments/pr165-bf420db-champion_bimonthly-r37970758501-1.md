## Experiment `pr165-bf420db-champion_bimonthly-r37970758501-1`: **PASSED GATES, did not beat champion**

Strategy `champion_bimonthly` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 42, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `aa7ed56c59d2796a`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0238 | 0.115441 | 0.113026 | 0.214663 | 9.6538 | 3675 |
| validation | 0.915 | 0.081726 | 0.091173 | 0.068719 | 8.7331 | 1593 |
| holdout | 1.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1441 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 570-bar reruns matched |
| min_trades_validation | pass | 1593 |
| max_drawdown_in_sample | pass | 0.214663 |
| max_vol_in_sample | pass | 0.113026 |
| max_drawdown_validation | pass | 0.068719 |
| max_vol_validation | pass | 0.091173 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.915 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.109 |
| turnover | pass | 8.7331 |
| robustness | pass | 1.031 |
| fill_participation | pass | 4e-05 |
