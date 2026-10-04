"""Daily factory status report, built deterministically (no Claude needed).

    python -m factory.report --ledger ledger/ --out status.md [--no-broker]

Reads the ledger branch checkout (experiments, executions), the champion, the Alpaca paper account
and the usage log, and writes one Markdown report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from factory.config import ROOT


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def _since(rows: list[dict], key: str, since: dt.datetime) -> list[dict]:
    out = []
    for r in rows:
        try:
            if dt.datetime.fromisoformat(str(r.get(key))) >= since:
                out.append(r)
        except ValueError:
            pass
    return out


def account_section(broker) -> list[str]:
    acct = broker.account()
    equity, last = float(acct["equity"]), float(acct.get("last_equity") or acct["equity"])
    hist = [float(x) for x in (broker.portfolio_history().get("equity") or []) if x]
    start = hist[0] if hist else equity
    peak = max(hist + [equity])
    positions = broker.positions()
    return [
        f"- Equity **${equity:,.0f}**; today {equity - last:+,.0f} ({(equity / last - 1) if last else 0:+.2%}); "
        f"since start of history {(equity / start - 1) if start else 0:+.2%}; drawdown from peak {1 - equity / peak:.1%}",
        f"- {len(positions)} open positions, cash ${float(acct['cash']):,.0f}",
    ]


def build(ledger: Path, broker=None, usage_table: str = "", hours: int = 24) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(hours=hours)
    champ = json.loads((ROOT / "state" / "champion.json").read_text())
    lines = [f"# Factory status {now:%Y-%m-%d %H:%M} UTC", "",
             f"**Champion:** `{champ.get('name')}` (experiment `{champ.get('experiment_id')}`, promoted {str(champ.get('promoted_at'))[:10]})", ""]

    lines.append("## Paper account")
    if broker is None:
        lines.append("- not checked")
    else:
        try:
            lines += account_section(broker)
        except Exception as e:  # report must still go out
            lines.append(f"- could not read account: {type(e).__name__}: {e}")

    ex = _since(_jsonl(ledger / "executions" / "index.jsonl"), "started_at", since)
    lines += ["", f"## Execution runs (last {hours}h): {len(ex)}"]
    lines += [f"- {r.get('started_at', '')[:16]} {r.get('status')}" for r in ex[-10:]] or ["- none"]

    exp = _since(_jsonl(ledger / "experiments" / "index.jsonl"), "evaluated_at", since)
    lines += ["", f"## Experiments evaluated (last {hours}h): {len(exp)}"]
    for r in exp[-20:]:
        verdict = "PROMOTE" if r.get("promote") else ("passed gates" if r.get("passed_gates") else "rejected")
        lines.append(f"- `{r.get('strategy')}`: {verdict}")
    if not exp:
        lines.append("- none")

    if usage_table:
        lines += ["", "## Claude usage (research runs)", usage_table]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", default="status.md")
    ap.add_argument("--usage-table", default="", help="file with the usage report table")
    ap.add_argument("--usage-issue", type=int, help="read usage events from this GitHub issue (e.g. 2)")
    ap.add_argument("--no-broker", action="store_true")
    a = ap.parse_args(argv)
    broker = None
    if not a.no_broker:
        from factory.broker import PaperBroker
        try:
            broker = PaperBroker()
        except Exception as e:
            print(f"broker unavailable: {e}", file=sys.stderr)
    usage = Path(a.usage_table).read_text() if a.usage_table and Path(a.usage_table).exists() else ""
    if not usage and a.usage_issue:
        import yaml
        from factory import usage as u
        try:
            usage = u.report(u._read_issue(a.usage_issue), yaml.safe_load(u.POLICY.read_text()))
        except Exception as e:
            usage = f"usage log unavailable: {e}"
    text = build(Path(a.ledger), broker, usage)
    Path(a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
