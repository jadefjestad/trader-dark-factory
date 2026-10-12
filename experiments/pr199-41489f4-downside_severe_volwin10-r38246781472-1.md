## Experiment `pr199-41489f4-downside_severe_volwin10-r38246781472-1`: **PASSED GATES, did not beat champion**

Strategy `downside_severe_volwin10` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 10, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1517 | 0.102792 | 0.088398 | 0.117219 | 12.1823 | 3802 |
| validation | 1.2085 | 0.119404 | 0.097981 | 0.068435 | 11.2676 | 1776 |
| holdout | 2.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2574 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1776 |
| max_drawdown_in_sample | pass | 0.117219 |
| max_vol_in_sample | pass | 0.088398 |
| max_drawdown_validation | pass | 0.068435 |
| max_vol_validation | pass | 0.097981 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.2085 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.057 |
| turnover | pass | 11.2676 |
| robustness | pass | 0.965 |
| fill_participation | pass | 4e-05 |
