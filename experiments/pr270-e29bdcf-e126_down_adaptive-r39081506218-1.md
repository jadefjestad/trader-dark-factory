## Experiment `pr270-e29bdcf-e126_down_adaptive-r39081506218-1`: **PASSED GATES, did not beat champion**

Strategy `e126_down_adaptive` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-16, fingerprint `b44d1ffe666fd947`, rules `e077534dd4d52fe1`

Beats champion `e63_lowcorr_every126` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9735 | 0.039669 | 0.040821 | 0.062741 | 6.4686 | 2761 |
| validation | 1.3402 | 0.117964 | 0.086192 | 0.05764 | 6.5319 | 1475 |
| holdout | 2.3 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.3184 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1475 |
| max_drawdown_in_sample | pass | 0.062741 |
| max_vol_in_sample | pass | 0.040821 |
| max_drawdown_validation | pass | 0.05764 |
| max_vol_validation | pass | 0.086192 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.3402 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.367 |
| turnover | pass | 6.5319 |
| robustness | pass | 0.982 |
| fill_participation | pass | 2e-05 |
