## Experiment `pr115-79ff464-overnight_momentum-r37367431980-3`: **PASSED GATES, did not beat champion**

Strategy `overnight_momentum` (1Day), params `{"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-05, fingerprint `09d3c531a4e21501`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.9012 | 0.11429 | 0.129485 | 0.222772 | 3.0494 | 541 |
| validation | 0.8371 | 0.081908 | 0.100573 | 0.104643 | 3.1857 | 231 |
| holdout | 1.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 29 experiments, probability the validation Sharpe beats luck is 0.1898 (luck benchmark 1.461 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 260-bar reruns matched |
| min_trades_validation | pass | 231 |
| max_drawdown_in_sample | pass | 0.222772 |
| max_vol_in_sample | pass | 0.129485 |
| max_drawdown_validation | pass | 0.104643 |
| max_vol_validation | pass | 0.100573 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8371 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.064 |
| turnover | pass | 3.1857 |
| robustness | pass | 0.999 |
| fill_participation | pass | 5e-05 |
