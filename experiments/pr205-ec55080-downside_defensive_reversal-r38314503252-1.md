## Experiment `pr205-ec55080-downside_defensive_reversal-r38314503252-1`: **PASSED GATES, did not beat champion**

Strategy `downside_defensive_reversal` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-12, fingerprint `709958ffc91b07e6`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0247 | 0.082118 | 0.080206 | 0.086932 | 6.5689 | 2651 |
| validation | 1.2094 | 0.122202 | 0.09989 | 0.073731 | 8.5055 | 1535 |
| holdout | 1.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2581 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1535 |
| max_drawdown_in_sample | pass | 0.086932 |
| max_vol_in_sample | pass | 0.080206 |
| max_drawdown_validation | pass | 0.073731 |
| max_vol_validation | pass | 0.09989 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.2094 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.185 |
| turnover | pass | 8.5055 |
| robustness | pass | 0.965 |
| fill_participation | pass | 3e-05 |
