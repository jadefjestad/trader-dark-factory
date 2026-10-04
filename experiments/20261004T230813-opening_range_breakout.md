## Experiment `20261004T230813-opening_range_breakout`: **REJECTED**

Strategy `opening_range_breakout` (15Min), params `{"range_bars": 2, "max_names": 8}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `3c4bdbf656f7d9f4`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -12.3398 | -0.630698 | 0.080457 | 0.771998 | 649.3899 | 24315 |
| validation | -10.4712 | -0.69044 | 0.111381 | 0.689515 | 654.5867 | 16743 |
| holdout | -14.7 |  |  | 0.7 |  |  |

Validation Sharpe vs others: benchmark SPY -5.3692

Selection-bias check (report only): after 23 experiments, probability the validation Sharpe beats luck is 0.0 (luck benchmark 0.386 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | **FAIL** | 15Min |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 30-bar reruns matched |
| min_trades_validation | pass | 16743 |
| max_drawdown_in_sample | **FAIL** | 0.771998 |
| max_vol_in_sample | pass | 0.080457 |
| max_drawdown_validation | **FAIL** | 0.689515 |
| max_vol_validation | pass | 0.111381 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -10.4712 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | -1.869 |
| turnover | pass | 654.5867 |
| robustness | **FAIL** | 0.0 |
| fill_participation | **FAIL** | 0.07153 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -18.455 |
