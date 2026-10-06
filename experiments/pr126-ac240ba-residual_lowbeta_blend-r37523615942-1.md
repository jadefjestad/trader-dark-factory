## Experiment `pr126-ac240ba-residual_lowbeta_blend-r37523615942-1`: **PASSED GATES, did not beat champion**

Strategy `residual_lowbeta_blend` (1Day), params `{"lookback": 252, "skip": 21, "beta_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "low_beta_share": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `a02241d089b64dc6`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.8552 | 0.091364 | 0.109317 | 0.204075 | 2.9893 | 819 |
| validation | 1.0455 | 0.097491 | 0.09288 | 0.067847 | 2.329 | 321 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 39 experiments, probability the validation Sharpe beats luck is 0.2434 (luck benchmark 1.546 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 321 |
| max_drawdown_in_sample | pass | 0.204075 |
| max_vol_in_sample | pass | 0.109317 |
| max_drawdown_validation | pass | 0.067847 |
| max_vol_validation | pass | 0.09288 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0455 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.19 |
| turnover | pass | 2.329 |
| robustness | pass | 0.984 |
| fill_participation | pass | 4e-05 |
