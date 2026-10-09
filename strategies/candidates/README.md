# Candidate strategies

The research agent writes one file per experiment here, e.g. `momentum_vol_filter.py`, containing
exactly one `Strategy` subclass. Allowed imports: `numpy`, `pandas`, `math`, `statistics`,
`strategies.base`. No file, network or process access (enforced by `factory/sandbox.py`).

Files stay here after a rejection so failed ideas remain visible in history; the full result of every
evaluation, pass or fail, is kept on the `ledger` branch.

## Setting `lookback`

`lookback` is the history the strategy is guaranteed live, and the `lookback_sufficient` gate reruns
the strategy on exactly that many bars. It must cover the longest signal window **plus** the longest
hold between rebalances, because a row that holds weights picked at an earlier rebalance needs the
signal as of that earlier bar. Example: residual momentum (252-bar beta, then 231 bars of residuals
shifted 21) needs 504 bars at the rebalance; held for up to 20 bars of a 21-bar cycle, it needs 524.
The champion `residual_lowcorr_reversal` declares 520, so copies of it fail `lookback_sufficient` on
weekly rebalances 17-20 bars after a monthly one (for example 2023-10-30 in #151, #152, #156). Copies
should declare `lookback = 545`. Live trading is not affected: `factory/execute.py` fetches about
1.6x the lookback (roughly 590 bars).
