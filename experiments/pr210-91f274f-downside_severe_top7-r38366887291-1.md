## Experiment `pr210-91f274f-downside_severe_top7-r38366887291-1`: **PROMOTE**

Strategy `downside_severe_top7` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-12, fingerprint `709958ffc91b07e6`, rules `e077534dd4d52fe1`

Beats champion `downside_corr_severe` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1609 | 0.099988 | 0.0853 | 0.10309 | 11.7431 | 3451 |
| validation | 1.2741 | 0.124175 | 0.096072 | 0.079023 | 10.7457 | 1621 |
| holdout | 2.3 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2873 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1621 |
| max_drawdown_in_sample | pass | 0.10309 |
| max_vol_in_sample | pass | 0.0853 |
| max_drawdown_validation | pass | 0.079023 |
| max_vol_validation | pass | 0.096072 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.2741 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.113 |
| turnover | pass | 10.7457 |
| robustness | pass | 0.97 |
| fill_participation | pass | 3e-05 |
