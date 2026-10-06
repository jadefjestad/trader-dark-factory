## Experiment `pr124-48c992c-intermediate_momentum-r37493103858-1`: **PASSED GATES, did not beat champion**

Strategy `intermediate_momentum` (1Day), params `{"far": 252, "near": 126, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `6a6c3339f2114acd`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9513 | 0.120895 | 0.12881 | 0.228781 | 4.4933 | 597 |
| validation | 0.4006 | 0.035729 | 0.100533 | 0.103287 | 4.2209 | 246 |
| holdout | 1.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 37 experiments, probability the validation Sharpe beats luck is 0.0561 (luck benchmark 1.531 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 300-bar reruns matched |
| min_trades_validation | pass | 246 |
| max_drawdown_in_sample | pass | 0.228781 |
| max_vol_in_sample | pass | 0.12881 |
| max_drawdown_validation | pass | 0.103287 |
| max_vol_validation | pass | 0.100533 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.4006 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.551 |
| turnover | pass | 4.2209 |
| robustness | pass | 1.09 |
| fill_participation | pass | 6e-05 |
