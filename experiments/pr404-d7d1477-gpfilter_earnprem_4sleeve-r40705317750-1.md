## Experiment `pr404-d7d1477-gpfilter_earnprem_4sleeve-r40705317750-1`: **PASSED GATES, did not beat champion**

Strategy `gpfilter_earnprem_4sleeve` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5, "window_start": 45, "window_end": 70}`
Data `alpaca:sip` 2016-01-04 to 2026-10-28, fingerprint `1301568e4a0ac64b`, rules `e077534dd4d52fe1`

Beats champion `gpfilter_wts_10_80_10` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.3343 | 0.037209 | 0.027757 | 0.025987 | 3.5034 | 3412 |
| validation | 2.2374 | 0.17346 | 0.072706 | 0.043512 | 3.8618 | 1606 |
| holdout | 2.0 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.7874 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1606 |
| max_drawdown_in_sample | pass | 0.025987 |
| max_vol_in_sample | pass | 0.027757 |
| max_drawdown_validation | pass | 0.043512 |
| max_vol_validation | pass | 0.072706 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 2.2374 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.903 |
| turnover | pass | 3.8618 |
| robustness | pass | 0.994 |
| fill_participation | pass | 3e-05 |
