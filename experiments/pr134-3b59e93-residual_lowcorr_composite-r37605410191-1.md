## Experiment `pr134-3b59e93-residual_lowcorr_composite-r37605410191-1`: **PASSED GATES, did not beat champion**

Strategy `residual_lowcorr_composite` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-06, fingerprint `a02241d089b64dc6`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_blend` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.7675 | 0.082839 | 0.111961 | 0.166098 | 2.9694 | 439 |
| validation | 1.0505 | 0.106492 | 0.102291 | 0.066668 | 3.2341 | 220 |
| holdout | 1.5 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 46 experiments, probability the validation Sharpe beats luck is 0.2242 (luck benchmark 1.592 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 220 |
| max_drawdown_in_sample | pass | 0.166098 |
| max_vol_in_sample | pass | 0.111961 |
| max_drawdown_validation | pass | 0.066668 |
| max_vol_validation | pass | 0.102291 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0505 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.283 |
| turnover | pass | 3.2341 |
| robustness | pass | 1.016 |
| fill_participation | pass | 5e-05 |
