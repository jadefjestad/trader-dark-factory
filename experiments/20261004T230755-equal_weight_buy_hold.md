## Experiment `20261004T230755-equal_weight_buy_hold`: **REJECTED**

Strategy `equal_weight_buy_hold` (1Day), params `{"rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.433 | 0.265242 | 0.17474 | 0.28528 | 0.4994 | 1204 |
| validation | 0.6686 | 0.112645 | 0.183899 | 0.208716 | 0.6467 | 523 |
| holdout | 1.5 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 23 experiments, probability the validation Sharpe beats luck is 0.155 (luck benchmark 1.391 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 30-bar reruns matched |
| min_trades_validation | pass | 523 |
| max_drawdown_in_sample | **FAIL** | 0.28528 |
| max_vol_in_sample | pass | 0.17474 |
| max_drawdown_validation | pass | 0.208716 |
| max_vol_validation | pass | 0.183899 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.6686 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.764 |
| turnover | pass | 0.6467 |
| robustness | pass | 0.989 |
| fill_participation | pass | 2e-05 |
