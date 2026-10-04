## Experiment `pr95-2bfe9a4-low_abnormal_shorting-r37244380251-1`: **REJECTED**

Strategy `low_abnormal_shorting` (1Day), params `{"signal_days": 20, "baseline_days": 250, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `ba364af48f82a7e9`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.095 | 0.143739 | 0.130219 | 0.271666 | 3.8535 | 1104 |
| validation | 0.7067 | 0.070542 | 0.10279 | 0.119086 | 8.2252 | 301 |
| holdout | 1.2 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 25 experiments, probability the validation Sharpe beats luck is 0.1593 (luck benchmark 1.416 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 320-bar reruns matched |
| min_trades_validation | pass | 301 |
| max_drawdown_in_sample | **FAIL** | 0.271666 |
| max_vol_in_sample | pass | 0.130219 |
| max_drawdown_validation | pass | 0.119086 |
| max_vol_validation | pass | 0.10279 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.7067 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.388 |
| turnover | pass | 8.2252 |
| robustness | pass | 1.089 |
| fill_participation | pass | 8e-05 |
