## Experiment `20261004T230800-cross_sectional_momentum`: **REJECTED**

Strategy `cross_sectional_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.21 | 0.284993 | 0.22917 | 0.311395 | 5.1236 | 541 |
| validation | 0.9106 | 0.170818 | 0.195494 | 0.163741 | 5.5103 | 228 |
| holdout | 1.3 |  |  | 0.3 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- short_term_reversal: 0.4746

Selection-bias check (report only): after 23 experiments, probability the validation Sharpe beats luck is 0.2507 (luck benchmark 1.391 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 260-bar reruns matched |
| min_trades_validation | pass | 228 |
| max_drawdown_in_sample | **FAIL** | 0.311395 |
| max_vol_in_sample | pass | 0.22917 |
| max_drawdown_validation | pass | 0.163741 |
| max_vol_validation | pass | 0.195494 |
| max_drawdown_holdout | **FAIL** | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9106 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.299 |
| turnover | pass | 5.5103 |
| robustness | pass | 0.934 |
| fill_participation | pass | 0.00013 |
