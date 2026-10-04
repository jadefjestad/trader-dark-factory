## Experiment `pr22-c0428f3-blend_ew_vol_momentum-r37182625038-1`: **PROMOTE**

Strategy `blend_ew_vol_momentum` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "ew_share": 0.5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `equal_weight_buy_hold` (validation + holdout Sharpe, margin per rules): **yes**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.3195 | 0.19556 | 0.143095 | 0.247874 | 1.9568 | 1123 |
| validation | 0.8062 | 0.107373 | 0.138325 | 0.135377 | 2.0852 | 492 |
| holdout | 1.5 |  |  | 0.2 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| min_trades_validation | pass | 492 |
| max_drawdown_in_sample | pass | 0.247874 |
| max_vol_in_sample | pass | 0.143095 |
| max_drawdown_validation | pass | 0.135377 |
| max_vol_validation | pass | 0.138325 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8062 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.513 |
| turnover | pass | 2.0852 |
| robustness | pass | 0.992 |
| fill_participation | pass | 3e-05 |
