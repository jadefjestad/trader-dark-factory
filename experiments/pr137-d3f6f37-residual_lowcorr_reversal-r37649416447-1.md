## Experiment `pr137-d3f6f37-residual_lowcorr_reversal-r37649416447-1`: **PROMOTE**

Strategy `residual_lowcorr_reversal` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-07, fingerprint `d482fa1e47c6cf6c`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_blend` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0284 | 0.108072 | 0.105238 | 0.188712 | 10.0909 | 3936 |
| validation | 1.0163 | 0.090496 | 0.089785 | 0.067858 | 8.9776 | 1700 |
| holdout | 2.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 49 experiments, probability the validation Sharpe beats luck is 0.2039 (luck benchmark 1.609 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 1700 |
| max_drawdown_in_sample | pass | 0.188712 |
| max_vol_in_sample | pass | 0.105238 |
| max_drawdown_validation | pass | 0.067858 |
| max_vol_validation | pass | 0.089785 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0163 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.012 |
| turnover | pass | 8.9776 |
| robustness | pass | 1.003 |
| fill_participation | pass | 4e-05 |
