## Experiment `20261004T054832-equal_weight_buy_hold`: **REJECTED**

Strategy `equal_weight_buy_hold` (1Day), params `{"rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `fab23ba5f9b8a9a5`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.4328 | 0.26519 | 0.174734 | 0.285211 | 0.5146 | 1549 |
| validation | 0.6686 | 0.112633 | 0.183886 | 0.208803 | 0.6584 | 625 |
| holdout | 1.5 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- sma_trend: 0.8533
- cross_sectional_momentum: 0.9109
- short_term_reversal: 0.4747

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| min_trades_validation | pass | 625 |
| max_drawdown_in_sample | **FAIL** | 0.285211 |
| max_vol_in_sample | pass | 0.174734 |
| max_drawdown_validation | pass | 0.208803 |
| max_vol_validation | pass | 0.183886 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6686 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.764 |
| turnover | pass | 0.6584 |
| robustness | pass | 0.989 |
| fill_participation | pass | 2e-05 |
