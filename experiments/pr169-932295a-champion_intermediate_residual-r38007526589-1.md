## Experiment `pr169-932295a-champion_intermediate_residual-r38007526589-1`: **PASSED GATES, did not beat champion**

Strategy `champion_intermediate_residual` (1Day), params `{"lookback": 252, "skip": 126, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0894 | 0.113193 | 0.103402 | 0.181757 | 10.1874 | 3947 |
| validation | 0.8643 | 0.074683 | 0.088048 | 0.065065 | 9.351 | 1747 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1274 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1747 |
| max_drawdown_in_sample | pass | 0.181757 |
| max_vol_in_sample | pass | 0.103402 |
| max_drawdown_validation | pass | 0.065065 |
| max_vol_validation | pass | 0.088048 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8643 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.225 |
| turnover | pass | 9.351 |
| robustness | pass | 1.016 |
| fill_participation | pass | 4e-05 |
