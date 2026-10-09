## Experiment `pr158-7526891-champion_biweekly_reversal-r37882112767-1`: **PASSED GATES, did not beat champion**

Strategy `champion_biweekly_reversal` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 10}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `1f6e9538633368a7`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9798 | 0.103686 | 0.106561 | 0.202716 | 7.7478 | 2656 |
| validation | 1.0873 | 0.0988 | 0.090478 | 0.066164 | 6.8551 | 1126 |
| holdout | 1.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2056 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1126 |
| max_drawdown_in_sample | pass | 0.202716 |
| max_vol_in_sample | pass | 0.106561 |
| max_drawdown_validation | pass | 0.066164 |
| max_vol_validation | pass | 0.090478 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0873 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.107 |
| turnover | pass | 6.8551 |
| robustness | pass | 1.011 |
| fill_participation | pass | 3e-05 |
