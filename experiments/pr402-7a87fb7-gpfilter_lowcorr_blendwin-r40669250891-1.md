## Experiment `pr402-7a87fb7-gpfilter_lowcorr_blendwin-r40669250891-1`: **PASSED GATES, did not beat champion**

Strategy `gpfilter_lowcorr_blendwin` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-27, fingerprint `abb7e3b6e31168a9`, rules `e077534dd4d52fe1`

Beats champion `gpfilter_wts_10_80_10` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9757 | 0.019868 | 0.020376 | 0.031582 | 3.2164 | 2435 |
| validation | 1.8291 | 0.118944 | 0.062599 | 0.035685 | 3.6932 | 1241 |
| holdout | 2.3 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.5862 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1241 |
| max_drawdown_in_sample | pass | 0.031582 |
| max_vol_in_sample | pass | 0.020376 |
| max_drawdown_validation | pass | 0.035685 |
| max_vol_validation | pass | 0.062599 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.8291 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.853 |
| turnover | pass | 3.6932 |
| robustness | pass | 0.998 |
| fill_participation | pass | 2e-05 |
