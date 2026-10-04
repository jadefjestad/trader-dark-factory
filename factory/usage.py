"""Self-managed Claude usage budget for the research Routine.

The Routine calls `start` first, reads the plan, does at most `tasks` backlog items, then calls `end`.
A run that starts and never ends is treated as having hit a usage limit: the next runs cool down and
shrink their batch. Runs that finish cleanly grow the batch toward the policy maximum, so the
subscription is used as fully as the policy allows.

    python -m factory.usage start --log ledger/usage/runs.jsonl   # prints a JSON plan
    python -m factory.usage end   --log ledger/usage/runs.jsonl --run-id ID --tasks 2
    python -m factory.usage report --log ledger/usage/runs.jsonl

Pass --issue N instead of --log to keep the log as comments on GitHub issue N (via the gh CLI).
That is what the Routine uses, because it can comment on issues but may not push to the ledger branch.
"""
from __future__ import annotations

import argparse
import re
import datetime as dt
import json
import sys
import uuid
from pathlib import Path

import yaml

from factory.config import ROOT

POLICY = ROOT / "agent" / "usage_policy.yaml"


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _read(log: Path) -> list[dict]:
    if not log.exists():
        return []
    return [json.loads(x) for x in log.read_text().splitlines() if x.strip()]


def runs(events: list[dict]) -> list[dict]:
    """Fold start/end events into one record per run."""
    by = {}
    for e in events:
        r = by.setdefault(e["run_id"], {"run_id": e["run_id"]})
        if e["event"] == "start":
            r["started"] = dt.datetime.fromisoformat(e["at"])
            r["tasks_allowed"] = e.get("tasks_allowed", 0)
        elif e["event"] == "end":
            r["ended"] = dt.datetime.fromisoformat(e["at"])
            r["tasks_done"] = e.get("tasks", 0)
            r["note"] = e.get("note", "")
    return sorted([r for r in by.values() if "started" in r], key=lambda r: r["started"])


def plan(events: list[dict], policy: dict, now=None) -> dict:
    now = now or _now()
    rs = runs(events)
    stale = dt.timedelta(minutes=policy["unfinished_after_minutes"])
    cut_off = [r for r in rs if "ended" not in r and now - r["started"] > stale]
    today = [r for r in rs if r["started"].date() == now.date()]
    window = [r for r in rs if now - r["started"] < dt.timedelta(hours=5)]
    tp = policy["tasks_per_run"]

    if cut_off and now - cut_off[-1]["started"] < dt.timedelta(hours=policy["cooldown_after_limit_hours"]):
        return {"go": False, "reason": f"cooling down: run {cut_off[-1]['run_id']} never finished (likely usage limit)", "tasks": 0}
    if len(today) >= policy["max_runs_per_day"]:
        return {"go": False, "reason": f"daily run budget used ({len(today)}/{policy['max_runs_per_day']})", "tasks": 0}
    if len(window) >= policy["max_runs_per_5h"]:
        return {"go": False, "reason": f"5-hour budget used ({len(window)}/{policy['max_runs_per_5h']})", "tasks": 0}

    # adapt batch size: shrink after a cut-off, grow after consecutive clean runs that used their whole allowance
    tasks = tp["start"]
    for r in rs:
        if "ended" not in r and now - r["started"] > stale:
            tasks = tp["min"]
        elif "ended" in r and r.get("tasks_done", 0) >= r.get("tasks_allowed", 0) > 0:
            tasks = min(tp["max"], r["tasks_allowed"] + 1)
        elif "ended" in r:
            tasks = max(tp["min"], r.get("tasks_allowed", tasks))
    return {"go": True, "reason": "within budget", "tasks": int(tasks),
            "runs_today": len(today), "runs_5h": len(window)}


def report(events: list[dict], policy: dict) -> str:
    rs = runs(events)
    days = {}
    for r in rs:
        d = days.setdefault(str(r["started"].date()), {"runs": 0, "tasks": 0, "cut_off": 0})
        d["runs"] += 1
        d["tasks"] += r.get("tasks_done", 0)
        d["cut_off"] += "ended" not in r
    lines = ["| Day | Runs | Cap | Utilisation | Tasks done | Unfinished |", "|---|---|---|---|---|---|"]
    cap = policy["max_runs_per_day"]
    for day, d in sorted(days.items())[-14:]:
        lines.append(f"| {day} | {d['runs']} | {cap} | {d['runs'] / cap:.0%} | {d['tasks']} | {d['cut_off']} |")
    return "\n".join(lines)


def _append(log: Path, event: dict):
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write(json.dumps(event) + "\n")


PREFIX = "usage-event "


def _read_issue(issue: int) -> list[dict]:
    import subprocess
    # REST, not `gh issue view`: GraphQL is unavailable from Claude Code cloud sessions
    out = subprocess.run(["gh", "api", "--paginate", f"repos/{{owner}}/{{repo}}/issues/{issue}/comments?per_page=100",
                          "--jq", ".[] | {body}"], capture_output=True, text=True, check=True).stdout
    return parse_comments(json.loads(line)["body"] for line in out.splitlines() if line.strip())


EVENT = re.compile(r"^" + re.escape(PREFIX) + r"`(\{.*?\})`", re.M)


def parse_comments(bodies) -> list[dict]:
    """Events from usage-log comments. Tolerates text appended after the event (e.g. a bot footer)."""
    events = []
    for body in bodies:
        m = EVENT.search(body or "")
        if m:
            try:
                events.append(json.loads(m.group(1)))
            except json.JSONDecodeError:
                pass
    return events


def _append_issue(issue: int, event: dict):
    import subprocess
    subprocess.run(["gh", "api", "-X", "POST", f"repos/{{owner}}/{{repo}}/issues/{issue}/comments",
                    "-f", f"body={PREFIX}`{json.dumps(event)}`"], check=True, capture_output=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["start", "end", "plan", "report"])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--log")
    src.add_argument("--issue", type=int)
    ap.add_argument("--run-id")
    ap.add_argument("--tasks", type=int, default=0)
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    policy = yaml.safe_load(POLICY.read_text())
    if a.issue:
        events = _read_issue(a.issue)
        append = lambda e: _append_issue(a.issue, e)
    else:
        events = _read(Path(a.log))
        append = lambda e: _append(Path(a.log), e)
    if a.cmd == "report":
        print(report(events, policy))
        return 0
    if a.cmd == "end":
        append({"event": "end", "run_id": a.run_id, "at": _now().isoformat(), "tasks": a.tasks, "note": a.note})
        return 0
    p = plan(events, policy)
    if a.cmd == "start" and p["go"]:
        p["run_id"] = a.run_id or f"{_now():%Y%m%dT%H%M}-{uuid.uuid4().hex[:6]}"
        append({"event": "start", "run_id": p["run_id"], "at": _now().isoformat(), "tasks_allowed": p["tasks"]})
    print(json.dumps(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
