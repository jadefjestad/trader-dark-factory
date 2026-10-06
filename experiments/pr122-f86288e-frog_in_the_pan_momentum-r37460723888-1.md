## Experiment `pr122-f86288e-frog_in_the_pan_momentum-r37460723888-1`: **PASSED GATES, did not beat champion**

Strategy `frog_in_the_pan_momentum` (1Day), params `{"lookback": 252, "skip": 21, "pool": 16, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-05, fingerprint `10db0e48279efbf2`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1342 | 0.147502 | 0.128711 | 0.210329 | 3.8262 | 570 |
| validation | 0.6269 | 0.0639 | 0.108742 | 0.11208 | 4.7388 | 238 |
| holdout | 1.2 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 35 experiments, probability the validation Sharpe beats luck is 0.1082 (luck benchmark 1.515 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 300-bar reruns matched |
| min_trades_validation | pass | 238 |
| max_drawdown_in_sample | pass | 0.210329 |
| max_vol_in_sample | pass | 0.128711 |
| max_drawdown_validation | pass | 0.11208 |
| max_vol_validation | pass | 0.108742 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6269 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.507 |
| turnover | pass | 4.7388 |
| robustness | pass | 1.033 |
| fill_participation | pass | 6e-05 |
