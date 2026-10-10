## Experiment `pr179-6c2af1d-champion_volwin10-r38082295089-1`: **PASSED GATES, did not beat champion**

Strategy `champion_volwin10` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 10, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `champion_volwin20` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1022 | 0.116178 | 0.104753 | 0.171639 | 12.3523 | 4050 |
| validation | 1.1456 | 0.106854 | 0.092812 | 0.064064 | 10.6687 | 1744 |
| holdout | 2.0 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2295 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1744 |
| max_drawdown_in_sample | pass | 0.171639 |
| max_vol_in_sample | pass | 0.104753 |
| max_drawdown_validation | pass | 0.064064 |
| max_vol_validation | pass | 0.092812 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.1456 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.043 |
| turnover | pass | 10.6687 |
| robustness | pass | 0.974 |
| fill_participation | pass | 4e-05 |
