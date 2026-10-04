"""Log every rule or limit change to the ledger (hard invariant; see factory/invariants.py).

CI runs this on every push to main. For each changed file under invariants.RULE_PATHS it records the
file, and for YAML files every changed key with its before and after value, plus the reason taken
from the commit message (or the merged PR's body) "Reason:" line.

    python scripts/rule_log.py --before <sha> --after <sha> --out out/
Writes out/rules-<after>.json when something changed; writes nothing otherwise.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from factory.invariants import RULE_PATHS  # noqa: E402

REASON = re.compile(r"^\s*\**reason\**\s*:\s*(.+)$", re.I | re.M)


def git(*args, check=True) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=check).stdout


def show(ref: str, path: str):
    out = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def flatten(d, prefix="") -> dict:
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}{k}."))
        return out
    return {prefix.rstrip("."): d}


def yaml_diff(before: str | None, after: str | None) -> list[dict]:
    b = flatten(yaml.safe_load(before) or {}) if before else {}
    a = flatten(yaml.safe_load(after) or {}) if after else {}
    return [{"key": k, "before": b.get(k), "after": a.get(k)}
            for k in sorted(set(a) | set(b)) if b.get(k) != a.get(k)]


def reason_for(after: str) -> str:
    m = REASON.search(git("log", "-1", "--format=%B", after))
    if m:
        return m.group(1).strip()
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        out = subprocess.run(["gh", "api", f"repos/{repo}/commits/{after}/pulls", "--jq", ".[0].body // \"\""],
                             capture_output=True, text=True)
        m = REASON.search(out.stdout or "")
        if m:
            return m.group(1).strip()
    return "(no reason given)"


def build(before: str, after: str) -> dict | None:
    if not before or set(before) == {"0"}:
        before = f"{after}^"
    status = [l.split("\t") for l in git("diff", "--name-status", before, after).splitlines() if l]
    files = []
    for parts in status:
        code, path = parts[0], parts[-1]
        if not path.startswith(RULE_PATHS) and not parts[1].startswith(RULE_PATHS):
            continue
        entry = {"file": path, "change": code[0]}
        if path.startswith(("protected/", "agent/")) and path.endswith((".yaml", ".yml")):
            entry["values"] = yaml_diff(show(before, parts[1]), show(after, path))
        files.append(entry)
    if not files:
        return None
    return {"kind": "rule_change", "commit": after, "previous": before,
            "changed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "reason": reason_for(after), "files": files}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default="")
    ap.add_argument("--after", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rec = build(a.before, a.after)
    if rec is None:
        print("no rule or limit changes")
        return 0
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    p = out / f"rules-{a.after[:12]}.json"
    p.write_text(json.dumps(rec, indent=2, default=str))
    print(p.read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
