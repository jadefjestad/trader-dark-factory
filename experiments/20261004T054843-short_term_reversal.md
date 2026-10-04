## Experiment `20261004T054843-short_term_reversal`: **REJECTED**

Strategy `short_term_reversal` (1Day), params `{"window": 5, "bottom_n": 8, "trend": 200, "rebalance_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `fab23ba5f9b8a9a5`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.2371 | 0.23354 | 0.183043 | 0.254484 | 62.1533 | 3299 |
| validation | 0.4747 | 0.070912 | 0.174323 | 0.22364 | 46.5534 | 1178 |
| holdout | 0.7 |  |  | 0.3 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8533
- cross_sectional_momentum: 0.9109

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| min_trades_validation | pass | 1178 |
| max_drawdown_in_sample | **FAIL** | 0.254484 |
| max_vol_in_sample | pass | 0.183043 |
| max_drawdown_validation | pass | 0.22364 |
| max_vol_validation | pass | 0.174323 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.4747 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.762 |
| turnover | **FAIL** | 46.5534 |
| robustness | pass | 0.786 |
| fill_participation | pass | 0.00037 |
