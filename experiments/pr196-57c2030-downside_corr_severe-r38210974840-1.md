## Experiment `pr196-57c2030-downside_corr_severe-r38210974840-1`: **PROMOTE**

Strategy `downside_corr_severe` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `volwin20_downside_corr` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2073 | 0.10512 | 0.085895 | 0.100124 | 11.231 | 3740 |
| validation | 1.2081 | 0.118746 | 0.097464 | 0.077175 | 10.2778 | 1753 |
| holdout | 2.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.257 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1753 |
| max_drawdown_in_sample | pass | 0.100124 |
| max_vol_in_sample | pass | 0.085895 |
| max_drawdown_validation | pass | 0.077175 |
| max_vol_validation | pass | 0.097464 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.2081 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.001 |
| turnover | pass | 10.2778 |
| robustness | pass | 0.965 |
| fill_participation | pass | 3e-05 |
