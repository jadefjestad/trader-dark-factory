## Experiment `pr83-1183bbe-strong_open_continuation-r37241596662-1`: **REJECTED**

Strategy `strong_open_continuation` (15Min), params `{"open_bars": 4, "min_open_move": 0.005, "names": 6}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `3c4bdbf656f7d9f4`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -2.7136 | -0.120423 | 0.04688 | 0.191119 | 80.5189 | 1810 |
| validation | -3.4976 | -0.18512 | 0.058047 | 0.20152 | 82.1602 | 1265 |
| holdout | -2.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY -5.3692
- opening_range_breakout: -10.4712

Selection-bias check (report only): after 24 experiments, probability the validation Sharpe beats luck is 0.0 (luck benchmark 0.39 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | **FAIL** | 15Min |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 60-bar reruns matched |
| min_trades_validation | pass | 1265 |
| max_drawdown_in_sample | pass | 0.191119 |
| max_vol_in_sample | pass | 0.04688 |
| max_drawdown_validation | pass | 0.20152 |
| max_vol_validation | pass | 0.058047 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -3.4976 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | 0.784 |
| turnover | pass | 82.1602 |
| robustness | **FAIL** | 0.0 |
| fill_participation | pass | 0.00125 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -5.394 |
