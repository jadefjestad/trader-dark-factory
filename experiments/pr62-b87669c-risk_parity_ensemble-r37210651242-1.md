## Experiment `pr62-b87669c-risk_parity_ensemble-r37210651242-1`: **REJECTED**

Strategy `risk_parity_ensemble` (1Day), params `{"lookback": 252, "skip": 21, "top_n": 8, "vol_target": 0.1, "vol_window": 60, "lowvol_window": 126, "lowvol_n": 10, "risk_window": 60, "rebalance_every": 21}`
Data `alpaca:sip` 2016-01-04 to 2026-10-02, fingerprint `7be6b82e83a6e13e`, rules `3b980fe320340be8`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.1071 | 0.149984 | 0.134336 | 0.236021 | 2.5903 | 1258 |
| validation | 0.7008 | 0.082834 | 0.123855 | 0.119239 | 2.2181 | 516 |
| holdout | 1.6 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 22 experiments, probability the validation Sharpe beats luck is 0.1724 (luck benchmark 1.378 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | **FAIL** | with only 520 bars (as live) signals differ at ['2020-11-06 00:00:00'] |
| min_trades_validation | pass | 516 |
| max_drawdown_in_sample | pass | 0.236021 |
| max_vol_in_sample | pass | 0.134336 |
| max_drawdown_validation | pass | 0.119239 |
| max_vol_validation | pass | 0.123855 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.7008 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.406 |
| turnover | pass | 2.2181 |
| robustness | pass | 1.009 |
| fill_participation | pass | 2e-05 |
