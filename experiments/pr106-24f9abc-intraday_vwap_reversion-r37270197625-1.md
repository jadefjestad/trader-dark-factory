## Experiment `pr106-24f9abc-intraday_vwap_reversion-r37270197625-1`: **REJECTED**

Strategy `intraday_vwap_reversion` (15Min), params `{"entry_gap": 0.005, "slots": 5, "weight": 0.1, "first_bar": 2, "last_entry_bar": 23}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `498e29287e6ccc46`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -7.257 | -0.292081 | 0.047442 | 0.402852 | 310.7367 | 6029 |
| validation | -7.3751 | -0.378863 | 0.064287 | 0.379069 | 346.5028 | 4849 |
| holdout | -8.2 |  |  | 0.4 |  |  |

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
| min_trades_validation | pass | 4849 |
| max_drawdown_in_sample | **FAIL** | 0.402852 |
| max_vol_in_sample | pass | 0.047442 |
| max_drawdown_validation | **FAIL** | 0.379069 |
| max_vol_validation | pass | 0.064287 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -7.3751 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | 0.118 |
| turnover | pass | 346.5028 |
| robustness | **FAIL** | 0.0 |
| fill_participation | **FAIL** | 0.39893 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -13.32 |
| latency_robustness | **FAIL** | fills 1 bar late: validation Sharpe -9.666 |
| order_budget | pass | peak 9 orders in one bar (limit 30/min), peak 45 a day (limit 500) |
