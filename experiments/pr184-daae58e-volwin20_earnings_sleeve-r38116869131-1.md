## Experiment `pr184-daae58e-volwin20_earnings_sleeve-r38116869131-1`: **PASSED GATES, did not beat champion**

Strategy `volwin20_earnings_sleeve` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5, "window_start": 45, "window_end": 70}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `champion_volwin20` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2988 | 0.125274 | 0.09455 | 0.131933 | 12.0453 | 4761 |
| validation | 1.1258 | 0.103198 | 0.091161 | 0.073783 | 10.7545 | 1976 |
| holdout | 1.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.2213 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1976 |
| max_drawdown_in_sample | pass | 0.131933 |
| max_vol_in_sample | pass | 0.09455 |
| max_drawdown_validation | pass | 0.073783 |
| max_vol_validation | pass | 0.091161 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.1258 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.173 |
| turnover | pass | 10.7545 |
| robustness | pass | 0.999 |
| fill_participation | pass | 3e-05 |
