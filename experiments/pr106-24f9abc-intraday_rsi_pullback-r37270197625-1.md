## Experiment `pr106-24f9abc-intraday_rsi_pullback-r37270197625-1`: **REJECTED**

Strategy `intraday_rsi_pullback` (15Min), params `{"rsi_bars": 6, "trend_bars": 26, "entry_rsi": 25.0, "exit_rsi": 55.0, "slots": 5, "weight": 0.1, "first_bar": 1, "last_entry_bar": 23}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `498e29287e6ccc46`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -16.1232 | -0.329403 | 0.024764 | 0.447354 | 316.2797 | 5058 |
| validation | -12.9245 | -0.34368 | 0.03254 | 0.341482 | 324.7365 | 3574 |
| holdout | -17.9 |  |  | 0.4 |  |  |

Validation Sharpe vs others: benchmark SPY -3.8066
- opening_range_breakout: -7.7045

Selection-bias check (report only): after 26 experiments, probability the validation Sharpe beats luck is 0.0 (luck benchmark 0.397 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | **FAIL** | 15Min |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 80-bar reruns matched |
| min_trades_validation | pass | 3574 |
| max_drawdown_in_sample | **FAIL** | 0.447354 |
| max_vol_in_sample | pass | 0.024764 |
| max_drawdown_validation | **FAIL** | 0.341482 |
| max_vol_validation | pass | 0.03254 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -12.9245 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | -3.199 |
| turnover | pass | 324.7365 |
| robustness | **FAIL** | 0.0 |
| fill_participation | **FAIL** | 1.18284 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -22.689 |
| latency_robustness | **FAIL** | fills 1 bar late: validation Sharpe -14.425 |
| order_budget | pass | peak 6 orders in one bar (limit 30/min), peak 38 a day (limit 500) |
