## Experiment `pr192-e2727ad-volwin20_lowcorr_heavy-r38178956997-1`: **PASSED GATES, did not beat champion**

Strategy `volwin20_lowcorr_heavy` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `champion_volwin20` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2072 | 0.126124 | 0.102828 | 0.157806 | 9.3326 | 4022 |
| validation | 1.0562 | 0.097117 | 0.092096 | 0.069668 | 7.9911 | 1696 |
| holdout | 1.9 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1936 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1696 |
| max_drawdown_in_sample | pass | 0.157806 |
| max_vol_in_sample | pass | 0.102828 |
| max_drawdown_validation | pass | 0.069668 |
| max_vol_validation | pass | 0.092096 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.0562 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.151 |
| turnover | pass | 7.9911 |
| robustness | pass | 1.0 |
| fill_participation | pass | 3e-05 |
