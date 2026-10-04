## Experiment `pr87-6530167-earnings_reaction_drift-r37243169062-1`: **REJECTED**

Strategy `earnings_reaction_drift` (1Day), params `{"hold_bars": 60, "min_reaction": 0.02, "slots": 8, "rebalance_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.3482 | 0.23055 | 0.162566 | 0.219438 | 7.3646 | 1577 |
| validation | 0.1085 | -0.000123 | 0.211324 | 0.360442 | 8.9711 | 762 |
| holdout | 1.1 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 24 experiments, probability the validation Sharpe beats luck is 0.0341 (luck benchmark 1.404 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 100-bar reruns matched |
| min_trades_validation | pass | 762 |
| max_drawdown_in_sample | pass | 0.219438 |
| max_vol_in_sample | pass | 0.162566 |
| max_drawdown_validation | **FAIL** | 0.360442 |
| max_vol_validation | pass | 0.211324 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | **FAIL** | 0.1085 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | **FAIL** | 1.24 |
| turnover | pass | 8.9711 |
| robustness | pass | 0.927 |
| fill_participation | pass | 0.00035 |
