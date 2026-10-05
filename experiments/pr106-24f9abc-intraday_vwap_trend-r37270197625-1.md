## Experiment `pr106-24f9abc-intraday_vwap_trend-r37270197625-1`: **REJECTED**

Strategy `intraday_vwap_trend` (15Min), params `{"entry_gap": 0.004, "slots": 5, "weight": 0.1, "first_bar": 2, "last_entry_bar": 23}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `498e29287e6ccc46`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -7.889 | -0.322432 | 0.049186 | 0.444593 | 363.8883 | 6867 |
| validation | -8.1017 | -0.425312 | 0.068083 | 0.428875 | 405.8457 | 5262 |
| holdout | -9.8 |  |  | 0.5 |  |  |

Validation Sharpe vs others: benchmark SPY -3.8066
- opening_range_breakout: -7.7045

Selection-bias check (report only): after 26 experiments, probability the validation Sharpe beats luck is 0.0 (luck benchmark 0.397 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | **FAIL** | 15Min |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 60-bar reruns matched |
| min_trades_validation | pass | 5262 |
| max_drawdown_in_sample | **FAIL** | 0.444593 |
| max_vol_in_sample | pass | 0.049186 |
| max_drawdown_validation | **FAIL** | 0.428875 |
| max_vol_validation | pass | 0.068083 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -8.1017 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | 0.213 |
| turnover | pass | 405.8457 |
| robustness | **FAIL** | 0.0 |
| fill_participation | **FAIL** | 0.13448 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -14.01 |
| latency_robustness | **FAIL** | fills 1 bar late: validation Sharpe -10.686 |
| order_budget | pass | peak 8 orders in one bar (limit 30/min), peak 58 a day (limit 500) |
