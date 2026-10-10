## Experiment `pr171-a5c5fcd-champion_invvol_weights-r38022986374-1`: **REJECTED**

Strategy `champion_invvol_weights` (1Day), params `{"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60, "reversal_window": 21, "reversal_every": 5}`
Data `alpaca:sip` 2016-01-04 to 2026-10-09, fingerprint `14d37b0249903c6c`, rules `e077534dd4d52fe1`

Beats champion `residual_lowcorr_reversal` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 1.0303 | 0.107977 | 0.104929 | 0.188625 | 10.8802 | 3961 |
| validation | 0.8452 | 0.076646 | 0.093452 | 0.078624 | 9.7148 | 1659 |
| holdout | 1.8 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 63 experiments, probability the validation Sharpe beats luck is 0.1228 (luck benchmark 1.676 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | **FAIL** | position weight 0.201 > 0.15 |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 545-bar reruns matched |
| min_trades_validation | pass | 1659 |
| max_drawdown_in_sample | pass | 0.188625 |
| max_vol_in_sample | pass | 0.104929 |
| max_drawdown_validation | pass | 0.078624 |
| max_vol_validation | pass | 0.093452 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.8452 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.185 |
| turnover | pass | 9.7148 |
| robustness | pass | 1.008 |
| fill_participation | pass | 7e-05 |
