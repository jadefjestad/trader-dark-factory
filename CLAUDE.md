# Trader Dark Factory: rules for Claude

This repo is an autonomous paper-trading research factory. Claude proposes; deterministic Python
decides and trades. Read `README.md` for the architecture.

## Hard rules
- Paper trading only. Never add code, URLs or credentials for live trading. CI fails on the live endpoint.
- Never edit `protected/`, `.github/`, `scripts/`, `strategies/base.py`, `strategies/baselines/`,
  existing tests, `agent/ROUTINE.md` or `agent/usage_policy.yaml`. CI's guard rejects this on
  `claude/*`, `agent/*` and `experiment/*` branches, and CODEOWNERS requires Jade's review.
- One experiment = one candidate file in `strategies/candidates/` with one measurable change.
- Candidates may import only numpy, pandas, math, statistics and `strategies.base`.
- Row t of a strategy's weights may only use data up to bar t. The evaluator proves this by rerunning
  on truncated data; peeking ahead fails the `no_lookahead` gate.
- Never delete candidate files or ledger records. Failed experiments are data.
- Do not try to tune against the holdout. Its figures are deliberately coarse.
- Do not write `state/champion.json` yourself except by copying the exact JSON an evaluation comment
  gives you; the evaluate check rejects anything else.

## Commands
- `python -m pytest -q`: tests
- `python scripts/guard.py`: repo guard
- `python -m factory.evaluate --candidate strategies/candidates/x.py --data synthetic`: smoke test
- `python -m factory.evaluate --baselines --data synthetic`: baseline leaderboard
- `python -m factory.usage start|end|report --issue N`: usage budget
