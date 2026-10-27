## Experiment `pr384-d310f5b-gpfilter_newsmood-r40424004352-1`: **PASSED GATES, did not beat champion**

Strategy `gpfilter_newsmood` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-26, fingerprint `ea24efd21c3325e4`, rules `e077534dd4d52fe1`

Beats champion `gpfilter_wts_10_80_10` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9997 | 0.032489 | 0.032514 | 0.034085 | 3.4612 | 2519 |
| validation | 1.3049 | 0.095178 | 0.071761 | 0.040848 | 3.7816 | 1310 |
| holdout | 2.4 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2981 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1310 |
| max_drawdown_in_sample | pass | 0.034085 |
| max_vol_in_sample | pass | 0.032514 |
| max_drawdown_validation | pass | 0.040848 |
| max_vol_validation | pass | 0.071761 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.3049 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.305 |
| turnover | pass | 3.7816 |
| robustness | pass | 0.995 |
| fill_participation | pass | 3e-05 |
