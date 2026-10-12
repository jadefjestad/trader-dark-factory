## Experiment `pr202-6bc8981-downside_blend_corr-r38288595825-1`: **PASSED GATES, did not beat champion**

Strategy `downside_blend_corr` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-12, fingerprint `3fbe2384e1ec2986`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2278 | 0.106142 | 0.085259 | 0.099927 | 11.2545 | 3755 |
| validation | 1.169 | 0.112475 | 0.095477 | 0.069672 | 10.1604 | 1749 |
| holdout | 2.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2398 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1749 |
| max_drawdown_in_sample | pass | 0.099927 |
| max_vol_in_sample | pass | 0.085259 |
| max_drawdown_validation | pass | 0.069672 |
| max_vol_validation | pass | 0.095477 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.169 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.059 |
| turnover | pass | 10.1604 |
| robustness | pass | 0.999 |
| fill_participation | pass | 3e-05 |
