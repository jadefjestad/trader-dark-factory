# Candidate strategies

The research agent writes one file per experiment here, e.g. `momentum_vol_filter.py`, containing
exactly one `Strategy` subclass. Allowed imports: `numpy`, `pandas`, `math`, `statistics`,
`strategies.base`. No file, network or process access (enforced by `factory/sandbox.py`).

Files stay here after a rejection so failed ideas remain visible in history; the full result of every
evaluation, pass or fail, is kept on the `ledger` branch.
