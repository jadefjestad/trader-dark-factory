"""Repository guard, run in CI on every PR and push. PROTECTED.

1. No live-trading endpoint anywhere in the repo.
2. Agent branches (experiment/*, agent/*) may not touch protected paths.
   (state/champion.json changes are verified separately by the evaluate workflow's verdict.)
3. Every candidate strategy passes the sandbox static check.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("GUARD_ROOT") or Path(__file__).resolve().parent.parent)
sys.path.insert(0, str(ROOT))

LIVE = re.compile(r"(?<![-.\w])api\.alpaca\.markets")
AGENT_BRANCH = re.compile(r"^(experiment|agent|claude)/")
AGENT_FORBIDDEN = ("protected/", ".github/", "scripts/", "strategies/base.py", "strategies/baselines/",
                   "agent/usage_policy.yaml", "agent/ROUTINE.md")


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def check_live_endpoints() -> list[str]:
    errs = []
    for p in git("ls-files").split():
        path = ROOT / p
        if p == "scripts/guard.py" or not path.is_file() or path.suffix in (".png", ".gz"):
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        if LIVE.search(text):
            errs.append(f"{p}: references the live trading endpoint")
    return errs


def check_branch(base: str, head_ref: str) -> list[str]:
    errs = []
    status = [line.split("\t") for line in git("diff", "--name-status", f"{base}...HEAD").splitlines() if line]
    changed = [parts[-1] for parts in status]
    bootstrap = subprocess.run(["git", "cat-file", "-e", f"{base}:scripts/guard.py"], cwd=ROOT, stderr=subprocess.DEVNULL).returncode != 0
    if bootstrap:
        print("guard: base branch has no guard yet (bootstrap PR); protected-path rule not applied")
    if AGENT_BRANCH.match(head_ref) and not bootstrap:
        for parts in status:
            code, f = parts[0], parts[-1]
            if f.startswith(AGENT_FORBIDDEN):
                errs.append(f"{f}: agent branch '{head_ref}' may not modify protected paths")
            elif f.startswith("tests/") and code[0] != "A":
                errs.append(f"{f}: agent branches may add tests but not change or delete existing ones")
    return errs


def check_candidates() -> list[str]:
    from factory.sandbox import CandidateRejected, check_source
    errs = []
    for p in sorted((ROOT / "strategies" / "candidates").glob("*.py")):
        if p.name == "__init__.py":
            continue
        try:
            check_source(p.read_text())
        except (CandidateRejected, SyntaxError) as e:
            errs.append(f"{p.relative_to(ROOT)}: {e}")
    return errs


def main() -> int:
    errs = check_live_endpoints() + check_candidates()
    base = os.environ.get("GUARD_BASE")       # e.g. origin/main, set on pull_request runs
    head_ref = os.environ.get("GUARD_HEAD_REF", "")
    if base:
        errs += check_branch(base, head_ref)
    for e in errs:
        print(f"GUARD: {e}")
    print("guard: ok" if not errs else f"guard: {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
