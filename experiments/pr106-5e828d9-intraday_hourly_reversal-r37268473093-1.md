## Experiment `pr106-5e828d9-intraday_hourly_reversal-r37268473093-1`: **REJECTED**

Strategy `intraday_hourly_reversal` (15Min), params `{"window": 6, "names": 5, "weight": 0.1}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `498e29287e6ccc46`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -14.7417 | -0.535739 | 0.051955 | 0.680092 | 644.238 | 9850 |
| validation | -10.7672 | -0.530195 | 0.06993 | 0.527411 | 645.3713 | 6656 |
| holdout | -14.0 |  |  | 0.6 |  |  |

Validation Sharpe vs others: benchmark SPY -3.8066
- opening_range_breakout: -7.7045

Selection-bias check (report only): after 26 experiments, probability the validation Sharpe beats luck is 0.0 (luck benchmark 0.397 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | **FAIL** | 15Min |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 40-bar reruns matched |
| min_trades_validation | pass | 6656 |
| max_drawdown_in_sample | **FAIL** | 0.680092 |
| max_vol_in_sample | pass | 0.051955 |
| max_drawdown_validation | **FAIL** | 0.527411 |
| max_vol_validation | pass | 0.06993 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -10.7672 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | -3.974 |
| turnover | pass | 645.3713 |
| robustness | **FAIL** | 0.0 |
| fill_participation | **FAIL** | 0.69033 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -18.392 |
| latency_robustness | **FAIL** | fills 1 bar late: validation Sharpe -10.609 |
| order_budget | pass | peak 10 orders in one bar (limit 30/min), peak 31 a day (limit 500) |
