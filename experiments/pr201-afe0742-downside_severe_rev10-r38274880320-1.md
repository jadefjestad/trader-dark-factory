## Experiment `pr201-afe0742-downside_severe_rev10-r38274880320-1`: **PASSED GATES, did not beat champion**

Strategy `downside_severe_rev10` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 10, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-12, fingerprint `ca6c771c7d51f1b8`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2695 | 0.111548 | 0.086285 | 0.101662 | 14.8252 | 4123 |
| validation | 0.9992 | 0.096772 | 0.097627 | 0.070393 | 12.8321 | 1861 |
| holdout | 2.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1723 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1861 |
| max_drawdown_in_sample | pass | 0.101662 |
| max_vol_in_sample | pass | 0.086285 |
| max_drawdown_validation | pass | 0.070393 |
| max_vol_validation | pass | 0.097627 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9992 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.27 |
| turnover | pass | 12.8321 |
| robustness | pass | 0.987 |
| fill_participation | pass | 4e-05 |
