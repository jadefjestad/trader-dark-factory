## Experiment `pr193-cb995a4-volwin20_downside_corr-r38186761844-1`: **PROMOTE**

Strategy `volwin20_downside_corr` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `champion_volwin20` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0768 | 0.112555 | 0.104217 | 0.161491 | 11.5637 | 4008 |
| validation | 1.1309 | 0.108033 | 0.094672 | 0.069674 | 10.5759 | 1746 |
| holdout | 2.1 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2234 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1746 |
| max_drawdown_in_sample | pass | 0.161491 |
| max_vol_in_sample | pass | 0.104217 |
| max_drawdown_validation | pass | 0.069674 |
| max_vol_validation | pass | 0.094672 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.1309 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.054 |
| turnover | pass | 10.5759 |
| robustness | pass | 0.996 |
| fill_participation | pass | 3e-05 |
