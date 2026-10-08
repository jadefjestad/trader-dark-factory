## Experiment `pr153-b5a4753-long_term_reversal-r37836797904-1`: **REJECTED**

Strategy `long_term_reversal` (1Day), params `{"formation": 756, "skip": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `563d11b61c7b435c`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.238 | 0.019288 | 0.103016 | 0.296421 | 1.7607 | 323 |
| validation | 1.6682 | 0.182579 | 0.103504 | 0.079829 | 2.895 | 219 |
| holdout | 1.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.4947 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 800-bar reruns matched |
| min_trades_validation | pass | 219 |
| max_drawdown_in_sample | **FAIL** | 0.296421 |
| max_vol_in_sample | pass | 0.103016 |
| max_drawdown_validation | pass | 0.079829 |
| max_vol_validation | pass | 0.103504 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.6682 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -1.43 |
| turnover | pass | 2.895 |
| robustness | pass | 1.007 |
| fill_participation | pass | 4e-05 |
