## Experiment `pr396-aec2201-gpfilter_resid_nobadnews-r40592000669-1`: **PASSED GATES, did not beat champion**

Strategy `gpfilter_resid_nobadnews` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-27, fingerprint `abb7e3b6e31168a9`, rules `e077534dd4d52fe1`

Beats champion `gpfilter_wts_10_80_10` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1983 | 0.034982 | 0.029047 | 0.031662 | 3.4545 | 2551 |
| validation | 2.1798 | 0.168131 | 0.072583 | 0.038347 | 3.7764 | 1316 |
| holdout | 2.6 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.7622 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1316 |
| max_drawdown_in_sample | pass | 0.031662 |
| max_vol_in_sample | pass | 0.029047 |
| max_drawdown_validation | pass | 0.038347 |
| max_vol_validation | pass | 0.072583 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 2.1798 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.982 |
| turnover | pass | 3.7764 |
| robustness | pass | 0.995 |
| fill_participation | pass | 3e-05 |
