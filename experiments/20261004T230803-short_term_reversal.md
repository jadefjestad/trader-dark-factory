## Experiment `20261004T230803-short_term_reversal`: **REJECTED**

Strategy `short_term_reversal` (1Day), params `{"window": 5, "bottom_n": 8, "trend": 200, "rebalance_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.237 | 0.233521 | 0.183033 | 0.254463 | 62.146 | 3172 |
| validation | 0.4746 | 0.070886 | 0.174316 | 0.22367 | 46.5463 | 1119 |
| holdout | 0.7 |  |  | 0.3 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106

Selection-bias check (report only): after 23 experiments, probability the validation Sharpe beats luck is 0.0999 (luck benchmark 1.391 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 210-bar reruns matched |
| min_trades_validation | pass | 1119 |
| max_drawdown_in_sample | **FAIL** | 0.254463 |
| max_vol_in_sample | pass | 0.183033 |
| max_drawdown_validation | pass | 0.22367 |
| max_vol_validation | pass | 0.174316 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.4746 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.762 |
| turnover | **FAIL** | 46.5463 |
| robustness | pass | 0.786 |
| fill_participation | pass | 0.00037 |
