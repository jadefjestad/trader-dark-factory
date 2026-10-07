## Experiment `pr129-838ecdd-low_beta_momentum-r37549946309-1`: **REJECTED**

Strategy `low_beta_momentum` (1Day), params `{"beta_window": 252, "pool": 16, "mom_lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `a02241d089b64dc6`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.7875 | 0.096397 | 0.127342 | 0.250982 | 4.9965 | 581 |
| validation | 0.9677 | 0.097642 | 0.10306 | 0.074436 | 3.0933 | 214 |
| holdout | 1.3 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 41 experiments, probability the validation Sharpe beats luck is 0.2065 (luck benchmark 1.56 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 300-bar reruns matched |
| min_trades_validation | pass | 214 |
| max_drawdown_in_sample | **FAIL** | 0.250982 |
| max_vol_in_sample | pass | 0.127342 |
| max_drawdown_validation | pass | 0.074436 |
| max_vol_validation | pass | 0.10306 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9677 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.18 |
| turnover | pass | 3.0933 |
| robustness | pass | 1.01 |
| fill_participation | pass | 8e-05 |
