## Experiment `pr437-2ab771d-invvolresid_stressrev-r41158275677-1`: **PASSED GATES, did not beat champion**

Strategy `invvolresid_stressrev` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-30, fingerprint `0dc99c3b3e413419`, rules `e077534dd4d52fe1`

Beats champion `invvol_calmresid` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1769 | 0.033559 | 0.028392 | 0.030856 | 3.6918 | 2502 |
| validation | 2.1457 | 0.148745 | 0.065718 | 0.037231 | 5.1596 | 1253 |
| holdout | 2.7 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.7472 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1253 |
| max_drawdown_in_sample | pass | 0.030856 |
| max_vol_in_sample | pass | 0.028392 |
| max_drawdown_validation | pass | 0.037231 |
| max_vol_validation | pass | 0.065718 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 2.1457 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.969 |
| turnover | pass | 5.1596 |
| robustness | pass | 0.995 |
| fill_participation | pass | 3e-05 |
