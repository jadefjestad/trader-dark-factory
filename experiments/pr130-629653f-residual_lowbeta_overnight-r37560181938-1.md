## Experiment `pr130-629653f-residual_lowbeta_overnight-r37560181938-1`: **PASSED GATES, did not beat champion**

Strategy `residual_lowbeta_overnight` (1Day), params `{"lookback": 252, "skip": 21, "beta_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "overnight_window": 252}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `a02241d089b64dc6`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9233 | 0.099854 | 0.10969 | 0.206032 | 2.8384 | 1057 |
| validation | 1.0151 | 0.092909 | 0.091634 | 0.072498 | 2.3693 | 378 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 42 experiments, probability the validation Sharpe beats luck is 0.2206 (luck benchmark 1.566 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 378 |
| max_drawdown_in_sample | pass | 0.206032 |
| max_vol_in_sample | pass | 0.10969 |
| max_drawdown_validation | pass | 0.072498 |
| max_vol_validation | pass | 0.091634 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0151 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.092 |
| turnover | pass | 2.3693 |
| robustness | pass | 0.99 |
| fill_participation | pass | 3e-05 |
