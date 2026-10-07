## Experiment `pr138-9d5097f-four_sleeve_overnight-r37664083632-1`: **PASSED GATES, did not beat champion**

Strategy `four_sleeve_overnight` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `19b28d1034019c97`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0262 | 0.110736 | 0.108109 | 0.195022 | 8.2754 | 4172 |
| validation | 0.9919 | 0.088412 | 0.090047 | 0.0714 | 7.4436 | 1739 |
| holdout | 1.9 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 50 experiments, probability the validation Sharpe beats luck is 0.1918 (luck benchmark 1.614 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 1739 |
| max_drawdown_in_sample | pass | 0.195022 |
| max_vol_in_sample | pass | 0.108109 |
| max_drawdown_validation | pass | 0.0714 |
| max_vol_validation | pass | 0.090047 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9919 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.034 |
| turnover | pass | 7.4436 |
| robustness | pass | 1.002 |
| fill_participation | pass | 3e-05 |
