## Experiment `pr90-8040a1f-residual_momentum_announcement_blend-r37243483853-1`: **PASSED GATES, did not beat champion**

Strategy `residual_momentum_announcement_blend` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "window_start": 45, "window_end": 70, "min_slots": 8, "premium_share": 0.5, "blend_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3c4bdbf656f7d9f4`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0269 | 0.114964 | 0.112709 | 0.183225 | 12.5678 | 2855 |
| validation | 0.9912 | 0.118965 | 0.120802 | 0.153321 | 12.6684 | 1220 |
| holdout | 1.4 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 24 experiments, probability the validation Sharpe beats luck is 0.2808 (luck benchmark 1.404 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 520-bar reruns matched |
| min_trades_validation | pass | 1220 |
| max_drawdown_in_sample | pass | 0.183225 |
| max_vol_in_sample | pass | 0.112709 |
| max_drawdown_validation | pass | 0.153321 |
| max_vol_validation | pass | 0.120802 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.9912 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.036 |
| turnover | pass | 12.6684 |
| robustness | pass | 0.998 |
| fill_participation | pass | 4e-05 |
