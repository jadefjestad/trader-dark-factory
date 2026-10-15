## Experiment `pr239-d5bec6e-ms63_lowcorr_every10-r38748465393-1`: **PASSED GATES, did not beat champion**

Strategy `ms63_lowcorr_every10` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-15, fingerprint `b32e0203952448ae`, rules `e077534dd4d52fe1`

Beats champion `w206020_minsevere63` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1879 | 0.058229 | 0.048645 | 0.062741 | 7.0617 | 2884 |
| validation | 1.1998 | 0.098197 | 0.081049 | 0.073056 | 8.709 | 1464 |
| holdout | 2.3 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2511 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1464 |
| max_drawdown_in_sample | pass | 0.062741 |
| max_vol_in_sample | pass | 0.048645 |
| max_drawdown_validation | pass | 0.073056 |
| max_vol_validation | pass | 0.081049 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.1998 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.012 |
| turnover | pass | 8.709 |
| robustness | pass | 0.974 |
| fill_participation | pass | 2e-05 |
