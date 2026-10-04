"""Hard invariants of the factory. These come from Jade's founding goal, not from the tunable rules in
protected/, and the guard keeps agent branches from editing or deleting this file and its tests.

- Paper trading only: the only broker endpoint is PAPER_URL; the live endpoint may appear nowhere.
- No orders when data, authentication or validation fails (factory/execute.py fails closed).
- Failed experiments are retained: candidate files on main are immutable; the ledger is append-only.
- Every change to rules or limits is logged to the ledger with before/after values and a reason
  (scripts/rule_log.py, run by CI on every push to main).
"""
from __future__ import annotations

PAPER_URL = "https://paper-api.alpaca.markets"
PAPER_ACCOUNT_PREFIX = "PA"
# Files whose changes are rule or limit changes and therefore logged to the ledger.
RULE_PATHS = ("protected/", "scripts/guard.py", "scripts/pr_verdict.py", ".github/", "strategies/base.py",
              "strategies/baselines/", "agent/usage_policy.yaml", "agent/ROUTINE.md", "factory/risk.py",
              "factory/invariants.py")
# Agent branches may not modify, rename or delete these.
INVARIANT_FILES = ("factory/invariants.py", "tests/test_invariants.py")


def require_paper(limits: dict, account_number: str) -> None:
    """Raise unless both the rules and the account say paper. Not configurable."""
    if limits.get("paper_only") is not True:
        raise RuntimeError("paper_only must be true; this factory never trades live")
    if not str(account_number).startswith(PAPER_ACCOUNT_PREFIX):
        raise RuntimeError("account is not an Alpaca paper account")
