## Experiment `pr159-3f4193f-champion_reversal_heavy-r37891631331-1`: **PASSED GATES, did not beat champion**

Strategy `champion_reversal_heavy` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `1f6e9538633368a7`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1046 | 0.115118 | 0.103547 | 0.178863 | 13.5301 | 3857 |
| validation | 0.9529 | 0.084884 | 0.090601 | 0.069489 | 12.1627 | 1652 |
| holdout | 2.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1556 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1652 |
| max_drawdown_in_sample | pass | 0.178863 |
| max_vol_in_sample | pass | 0.103547 |
| max_drawdown_validation | pass | 0.069489 |
| max_vol_validation | pass | 0.090601 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9529 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.152 |
| turnover | pass | 12.1627 |
| robustness | pass | 1.007 |
| fill_participation | pass | 6e-05 |
