# Trader Dark Factory: rules for Claude

This repo is an autonomous paper-trading research factory. Claude proposes; deterministic Python
decides and trades. Read `README.md` for the architecture.

## Hard rules
- Paper trading only. Never add code, URLs or credentials for live trading. CI fails on the live endpoint.
- You manage everything, rules and limits included, and merge your own PRs once CI is green
  (Jade, 2026-10-04). A PR that changes rules or limits (`factory.invariants.RULE_PATHS`) needs a
  `Reason:` line in its body; CI logs the before/after values to the ledger on merge.
- Never modify or delete `factory/invariants.py` or `tests/test_invariants.py` (hard invariants: paper
  only, fail closed, failed experiments kept, rule changes logged). Add invariant tests in new files.
- One experiment = one candidate file in `strategies/candidates/` with one measurable change.
- Candidates may import only numpy, pandas, math, statistics and `strategies.base`.
- Row t of a strategy's weights may only use data up to bar t. The evaluator proves this by rerunning
  on truncated data; peeking ahead fails the `no_lookahead` gate.
- Never delete candidate files or ledger records. Failed experiments are data. Candidate files already
  on main are immutable (CI rejects edits, deletes and renames); improve an idea in a new file.
- A weight row that is entirely NaN means "hold" (no trades). Any other NaN is a bug.
- Do not try to tune against the holdout. Its figures are deliberately coarse.
- Do not write `state/champion.json` yourself except by copying the exact JSON an evaluation comment
  gives you; the evaluate check rejects anything else.

## Commands
- `python -m pytest -q`: tests
- `python scripts/guard.py`: repo guard
- `python -m factory.evaluate --candidate strategies/candidates/x.py --data synthetic`: smoke test
- `python -m factory.evaluate --baselines --data synthetic`: baseline leaderboard
- `python -m factory.usage start|end|report --issue N`: usage budget
