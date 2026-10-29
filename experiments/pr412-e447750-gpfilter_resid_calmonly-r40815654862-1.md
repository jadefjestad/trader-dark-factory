## Experiment `pr412-e447750-gpfilter_resid_calmonly-r40815654862-1`: **PASSED GATES, did not beat champion**

Strategy `gpfilter_resid_calmonly` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-28, fingerprint `002dcc58dc0e957f`, rules `e077534dd4d52fe1`

Beats champion `gpfilter_wts_10_80_10` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0796 | 0.031046 | 0.028703 | 0.031582 | 3.3933 | 2479 |
| validation | 2.2537 | 0.1581 | 0.066177 | 0.03606 | 3.452 | 1213 |
| holdout | 2.5 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.7939 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1213 |
| max_drawdown_in_sample | pass | 0.031582 |
| max_vol_in_sample | pass | 0.028703 |
| max_drawdown_validation | pass | 0.03606 |
| max_vol_validation | pass | 0.066177 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 2.2537 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -1.174 |
| turnover | pass | 3.452 |
| robustness | pass | 0.997 |
| fill_participation | pass | 3e-05 |
