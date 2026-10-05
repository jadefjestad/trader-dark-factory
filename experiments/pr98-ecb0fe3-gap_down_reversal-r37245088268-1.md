## Experiment `pr98-ecb0fe3-gap_down_reversal-r37245088268-1`: **REJECTED**

Strategy `gap_down_reversal` (15Min), params `{"min_gap": 0.015, "max_names": 6}`
Data `alpaca:sip` 2022-12-19 to 2026-10-02, fingerprint `cb56a692d8abf930`, rules `e388c160c85ccbdc`


| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | -0.5812 | -0.016833 | 0.02851 | 0.050903 | 24.3683 | 833 |
| validation | -1.0096 | -0.065945 | 0.065454 | 0.073726 | 43.47 | 1200 |
| holdout | -1.5 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY -3.8066
- opening_range_breakout: -7.7045

Selection-bias check (report only): after 26 experiments, probability the validation Sharpe beats luck is 0.0015 (luck benchmark 0.397 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | **FAIL** | 15Min |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 60-bar reruns matched |
| min_trades_validation | pass | 1200 |
| max_drawdown_in_sample | pass | 0.050903 |
| max_vol_in_sample | pass | 0.02851 |
| max_drawdown_validation | pass | 0.073726 |
| max_vol_validation | pass | 0.065454 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | -1.0096 |
| min_holdout_sharpe | **FAIL** | hidden |
| sharpe_decay | pass | 0.428 |
| turnover | pass | 43.47 |
| robustness | **FAIL** | 0.0 |
| fill_participation | pass | 0.0007 |
| cost_stress | **FAIL** | 2.0x costs: validation Sharpe -1.781 |
