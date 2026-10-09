## Experiment `pr162-976e94c-ltr_lowcorr_reversal-r37927712167-1`: **PASSED GATES, did not beat champion**

Strategy `ltr_lowcorr_reversal` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5, "ltr_formation": 756, "ltr_skip": 252}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `1f6e9538633368a7`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0317 | 0.099299 | 0.09632 | 0.208276 | 9.4168 | 3696 |
| validation | 1.3444 | 0.120427 | 0.087614 | 0.070072 | 8.7569 | 1724 |
| holdout | 1.6 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.3226 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 800-bar reruns matched |
| min_trades_validation | pass | 1724 |
| max_drawdown_in_sample | pass | 0.208276 |
| max_vol_in_sample | pass | 0.09632 |
| max_drawdown_validation | pass | 0.070072 |
| max_vol_validation | pass | 0.087614 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.3444 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.313 |
| turnover | pass | 8.7569 |
| robustness | pass | 1.0 |
| fill_participation | pass | 4e-05 |
