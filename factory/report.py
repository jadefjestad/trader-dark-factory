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


ASSUMED_COST_BPS_KEYS = ("slippage_bps", "half_spread_bps")


def execution_quality(ledger: Path, broker, days: int = 7) -> list[str]:
    """Realised fill cost versus the price the executor sized orders on, against the backtest's assumption.

    Cost is signed against us: a buy filled above the decision price or a sell filled below it is positive."""
    from factory import config
    cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    refs = {}
    for f in sorted((ledger / "executions").glob("*.json")):
        try:
            r = json.loads(f.read_text())
            if dt.datetime.fromisoformat(str(r.get("started_at"))) < cut:
                continue
        except (ValueError, OSError):
            continue
        for o in r.get("submitted") or []:
            px = (r.get("prices") or {}).get(o.get("symbol"))
            if px:
                refs[o["client_order_id"]] = (o["side"], float(px))
    if not refs:
        return [f"- no submitted orders in the last {days} days"]
    filled = {o.get("client_order_id"): float(o["filled_avg_price"]) for o in broker.closed_orders(cut.date().isoformat())
              if o.get("filled_avg_price") and o.get("client_order_id") in refs}
    if not filled:
        return [f"- {len(refs)} orders submitted, none reported filled yet"]
    bps = sorted(((p / refs[c][1] - 1) * (1 if refs[c][0] == "buy" else -1) * 1e4) for c, p in filled.items())
    costs = config.evaluation()["costs"]["1Day"]
    assumed = sum(float(costs[k]) for k in ASSUMED_COST_BPS_KEYS)
    mean = sum(bps) / len(bps)
    flag = " **(above the backtest assumption)**" if mean > assumed else ""
    return [f"- {len(bps)} fills in the last {days} days: mean cost {mean:+.1f} bps, median {bps[len(bps) // 2]:+.1f} bps "
            f"vs {assumed:.0f} bps assumed per side{flag}"]


def build(ledger: Path, broker=None, usage_table: str = "", hours: int = 24, fund_brokers: dict | None = None) -> str:
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

    if fund_brokers is not None:
        from factory import readme
        lines += [""] + ["## Funds" if x == "### Fund leaderboard" else x
                         for x in readme.fund_section(readme.executions(ledger), fund_brokers)]

    if broker is not None:
        lines += ["", "## Execution quality (fills vs decision prices)"]
        try:
            lines += execution_quality(ledger, broker)
        except Exception as e:
            lines.append(f"- could not compute: {type(e).__name__}: {e}")

    ex = _since(_jsonl(ledger / "executions" / "index.jsonl"), "started_at", since)
    lines += ["", f"## Execution runs (last {hours}h): {len(ex)}"]
    lines += [f"- {r.get('started_at', '')[:16]} {'fund ' + str(r['fund']) + ': ' if r.get('fund') else ''}{r.get('status')}"
              for r in ex[-20:]] or ["- none"]

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
    broker, brokers = None, None
    if not a.no_broker:
        from factory import funds
        from factory.broker import PaperBroker
        try:
            broker = PaperBroker()
        except Exception as e:
            print(f"broker unavailable: {e}", file=sys.stderr)
        brokers = {}
        for n in range(1, funds.MAX_FUNDS + 1):
            if creds := funds.credentials(n):
                try:
                    brokers[n] = PaperBroker(*creds)
                except Exception as e:
                    print(f"fund {n} broker unavailable: {e}", file=sys.stderr)
    usage = Path(a.usage_table).read_text() if a.usage_table and Path(a.usage_table).exists() else ""
    if not usage and a.usage_issue:
        import yaml
        from factory import usage as u
        try:
            usage = u.report(u._read_issue(a.usage_issue), yaml.safe_load(u.POLICY.read_text()))
        except Exception as e:
            usage = f"usage log unavailable: {e}"
    text = build(Path(a.ledger), broker, usage, fund_brokers=brokers)
    Path(a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
