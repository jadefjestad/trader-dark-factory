## Experiment `pr151-58e27cf-champion_quality_sleeve-r37806116432-1`: **REJECTED**

Strategy `champion_quality_sleeve` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-08, fingerprint `7cc7e6ccd830c388`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.095 | 0.11804 | 0.107115 | 0.192944 | 8.0914 | 4189 |
| validation | 0.8933 | 0.078007 | 0.088804 | 0.067673 | 6.9674 | 1769 |
| holdout | 1.7 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 61 experiments, probability the validation Sharpe beats luck is 0.1395 (luck benchmark 1.668 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | **FAIL** | with only 520 bars (as live) signals differ at ['2023-10-30 00:00:00'] |
| min_trades_validation | pass | 1769 |
| max_drawdown_in_sample | pass | 0.192944 |
| max_vol_in_sample | pass | 0.107115 |
| max_drawdown_validation | pass | 0.067673 |
| max_vol_validation | pass | 0.088804 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8933 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.202 |
| turnover | pass | 6.9674 |
| robustness | pass | 1.001 |
| fill_participation | pass | 3e-05 |
