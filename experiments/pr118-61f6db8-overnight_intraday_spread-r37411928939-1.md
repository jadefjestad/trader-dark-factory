## Experiment `pr118-61f6db8-overnight_intraday_spread-r37411928939-1`: **PASSED GATES, did not beat champion**

Strategy `overnight_intraday_spread` (1Day), params `{"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.1, "vol_window": 60}`
Data `alpaca:sip` 2016-01-04 to 2026-10-05, fingerprint `10db0e48279efbf2`, rules `e077534dd4d52fe1`

Beats champion `residual_vol_momentum` (validation + holdout Sharpe, margin per rules): **no**

| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |
|---|---|---|---|---|---|---|
| in_sample | 0.8603 | 0.107692 | 0.128593 | 0.241259 | 3.4155 | 557 |
| validation | 0.5072 | 0.04708 | 0.101053 | 0.129628 | 2.7695 | 214 |
| holdout | 1.4 |  |  | 0.1 |  |  |

Validation Sharpe vs others: benchmark SPY 0.1826
- equal_weight_buy_hold: 0.6686
- sma_trend: 0.8542
- cross_sectional_momentum: 0.9106
- short_term_reversal: 0.4746

Selection-bias check (report only): after 31 experiments, probability the validation Sharpe beats luck is 0.0848 (luck benchmark 1.48 annual).

| Gate | Result | Detail |
|---|---|---|
| data_not_synthetic | pass | alpaca:sip |
| executable_timeframe (promotion only) | pass | 1Day |
| risk_limits | pass | ok |
| no_lookahead | pass | 5 truncated reruns matched |
| lookback_sufficient | pass | 5 260-bar reruns matched |
| min_trades_validation | pass | 214 |
| max_drawdown_in_sample | pass | 0.241259 |
| max_vol_in_sample | pass | 0.128593 |
| max_drawdown_validation | pass | 0.129628 |
| max_vol_validation | pass | 0.101053 |
| max_drawdown_holdout | pass | hidden |
| max_vol_holdout | pass | hidden |
| min_validation_sharpe | pass | 0.5072 |
| min_holdout_sharpe | pass | hidden |
| sharpe_decay | pass | 0.353 |
| turnover | pass | 2.7695 |
| robustness | pass | 0.971 |
| fill_participation | pass | 6e-05 |
