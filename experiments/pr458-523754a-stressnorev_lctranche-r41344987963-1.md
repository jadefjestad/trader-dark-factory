## Experiment `pr458-523754a-stressnorev_lctranche-r41344987963-1`: **PASSED GATES, did not beat champion**

Strategy `stressnorev_lctranche` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-30, fingerprint `0dc99c3b3e413419`, rules `e077534dd4d52fe1`

Beats champion `invvolresid_lcrankwt` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2782 | 0.03679 | 0.028587 | 0.030856 | 3.297 | 2368 |
| validation | 2.0002 | 0.131545 | 0.06286 | 0.04063 | 2.1718 | 828 |
| holdout | 2.7 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.6764 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 828 |
| max_drawdown_in_sample | pass | 0.030856 |
| max_vol_in_sample | pass | 0.028587 |
| max_drawdown_validation | pass | 0.04063 |
| max_vol_validation | pass | 0.06286 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 2.0002 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.722 |
| turnover | pass | 2.1718 |
| robustness | pass | 0.993 |
| fill_participation | pass | 2e-05 |
