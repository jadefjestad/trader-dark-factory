## Experiment `pr87-6530167-earnings_announcement_premium-r37243169062-1`: **PASSED GATES, did not beat champion**

Strategy `earnings_announcement_premium` (1Day), params `{"window_start": 45, "window_end": 70, "min_slots": 8, "rebalance_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.514 | 0.19334 | 0.122401 | 0.131059 | 21.7611 | 2146 |
| validation | 0.9672 | 0.148728 | 0.155264 | 0.228279 | 22.2085 | 847 |
| holdout | 0.8 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 24 experiments, probability the validation Sharpe beats luck is 0.2682 (luck benchmark 1.404 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 120-bar reruns matched |
| min_trades_validation | pass | 847 |
| max_drawdown_in_sample | pass | 0.131059 |
| max_vol_in_sample | pass | 0.122401 |
| max_drawdown_validation | pass | 0.228279 |
| max_vol_validation | pass | 0.155264 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9672 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.547 |
| turnover | pass | 22.2085 |
| robustness | pass | 0.992 |
| fill_participation | pass | 0.00012 |
