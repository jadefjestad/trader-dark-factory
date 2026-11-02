## Experiment `pr464-0450876-lcrankwt_regimerefresh-r41410916349-1`: **PASSED GATES, did not beat champion**

Strategy `lcrankwt_regimerefresh` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 20, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-30, fingerprint `0dc99c3b3e413419`, rules `e077534dd4d52fe1`

Beats champion `invvolresid_lcrankwt` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0227 | 0.034371 | 0.033597 | 0.042797 | 3.8281 | 2519 |
| validation | 1.6503 | 0.11182 | 0.065637 | 0.056843 | 3.8534 | 1187 |
| holdout | 2.4 |  |  | 0.0 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4747

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.4844 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1187 |
| max_drawdown_in_sample | pass | 0.042797 |
| max_vol_in_sample | pass | 0.033597 |
| max_drawdown_validation | pass | 0.056843 |
| max_vol_validation | pass | 0.065637 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 1.6503 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | -0.628 |
| turnover | pass | 3.8534 |
| robustness | pass | 0.986 |
| fill_participation | pass | 3e-05 |
