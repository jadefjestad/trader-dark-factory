"""Fund equity snapshots and the performance chart in the README.

    python -m factory.equity snapshot --out out/     # one snapshot of every funded account (Actions, 4x a trading day)
    python -m factory.equity chart --ledger ledger/ --out funds.svg

A snapshot records each fund's equity and the strategy it runs at that moment, plus the SPY price for
the Spyder-man benchmark. .github/workflows/snapshot.yml appends one to the ledger branch (`equity/`)
four times each trading day. The chart draws the last 90 days of snapshots as % change from each line's
first point in the window, with the benchmark highlighted and a marker wherever a fund's strategy
changed. Plain SVG with no dependencies; needs no Claude.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from html import escape
from pathlib import Path

WINDOW_DAYS = 90
# categorical slots 1-8 (dataviz reference palette, light / dark); fund 9 takes a muted gray
LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948", "#8a8984"]
DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767", "#8f8e88"]


# ---------------------------------------------------------------- snapshots

def snapshot(fund_list, brokers: dict, now: dt.datetime | None = None) -> dict | None:
    """One reading of every fund. None when the market is closed (nothing worth plotting)."""
    from factory import funds as fmod
    now = now or dt.datetime.now(dt.timezone.utc)
    rec = {"taken_at": now.isoformat(timespec="seconds"), "funds": {}}
    any_broker = next(iter(brokers.values()), None)
    if any_broker is None:
        return None
    if not any_broker.clock().get("is_open"):
        return None
    for f in fund_list:
        if f.benchmark:
            sym = f.benchmark["symbol"]
            try:
                px = any_broker.latest_trades([sym])[sym][0]
                rec["funds"][str(f.number)] = {"price": float(px), "strategy": f"{sym} benchmark"}
            except Exception as e:
                rec["funds"][str(f.number)] = {"error": f"{type(e).__name__}: {e}"[:200]}
            continue
        b = brokers.get(f.number)
        if b is None:
            continue
        try:
            strat = fmod.strategy(f)["name"]
        except Exception:
            strat = "invalid assignment"
        try:
            rec["funds"][str(f.number)] = {"equity": float(b.account()["equity"]), "strategy": strat}
        except Exception as e:
            rec["funds"][str(f.number)] = {"error": f"{type(e).__name__}: {e}"[:200], "strategy": strat}
    return rec


def _brokers() -> dict:
    from factory import funds
    from factory.broker import PaperBroker
    out = {}
    for f in funds.load():
        if not f.benchmark and (creds := funds.credentials(f.number)):
            try:
                out[f.number] = PaperBroker(*creds)
            except Exception as e:
                print(f"fund {f.number} broker unavailable: {e}", file=sys.stderr)
    return out


# ---------------------------------------------------------------- series

def load(ledger: Path, now: dt.datetime | None = None, days: int = WINDOW_DAYS) -> list[dict]:
    now = now or dt.datetime.now(dt.timezone.utc)
    cut = now - dt.timedelta(days=days)
    recs = []
    for p in sorted((ledger / "equity").glob("*.json")):
        try:
            r = json.loads(p.read_text())
            if dt.datetime.fromisoformat(r["taken_at"]) >= cut:
                recs.append(r)
        except (OSError, ValueError, KeyError):
            continue
    return sorted(recs, key=lambda r: r["taken_at"])


def series(recs: list[dict]) -> tuple[dict, list[dict]]:
    """{fund: [(snapshot index, % change)]} indexed to each fund's first reading, and strategy changes."""
    lines: dict[int, list] = {}
    base: dict[int, float] = {}
    last_strategy: dict[int, str] = {}
    changes = []
    for i, r in enumerate(recs):
        for k, v in (r.get("funds") or {}).items():
            n = int(k)
            val = v.get("equity", v.get("price"))
            if val is None or val <= 0:
                continue
            base.setdefault(n, float(val))
            pct = float(val) / base[n] - 1
            lines.setdefault(n, []).append((i, pct))
            s = v.get("strategy")
            if s and n in last_strategy and s != last_strategy[n]:
                changes.append({"fund": n, "index": i, "pct": pct, "taken_at": r["taken_at"],
                                "from": last_strategy[n], "to": s})
            if s:
                last_strategy[n] = s
    return lines, changes


# ---------------------------------------------------------------- SVG

def svg(recs: list[dict], fund_list, width: int = 900, height: int = 480) -> str:
    lines, changes = series(recs)
    labels = {f.number: f.label for f in fund_list}
    bench = {f.number for f in fund_list if f.benchmark}
    left, right, top, bottom = 56, 110, 44, 102
    pw, ph = width - left - right, height - top - bottom
    n = max(len(recs), 2)
    vals = [p for pts in lines.values() for _, p in pts] or [0.0]
    lo, hi = min(vals + [0.0]), max(vals + [0.0])
    pad = max((hi - lo) * 0.1, 0.005)
    lo, hi = lo - pad, hi + pad
    x = lambda i: left + pw * i / (n - 1)
    y = lambda p: top + ph * (hi - p) / (hi - lo)

    css_vars = "".join(f"--s{k}:{c};" for k, c in enumerate(LIGHT, 1))
    css_dark = "".join(f"--s{k}:{c};" for k, c in enumerate(DARK, 1))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           f'role="img" aria-label="Fund performance, % change over the last {WINDOW_DAYS} days">',
           "<style>",
           f":root{{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e4e3df;{css_vars}}}",
           f"@media (prefers-color-scheme: dark){{:root{{--bg:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--grid:#383835;{css_dark}}}}}",
           "text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:var(--ink2);font-size:12px}",
           ".t{fill:var(--ink);font-size:15px;font-weight:600}.l{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}",
           ".b{fill:none;stroke:var(--ink);stroke-width:3.5;stroke-linejoin:round;stroke-linecap:round}",
           "</style>",
           f'<rect width="{width}" height="{height}" fill="var(--bg)"/>',
           f'<text class="t" x="{left}" y="24">Fund performance: % change over the last {WINDOW_DAYS} days</text>']
    # recessive grid and y labels
    step = _nice_step(hi - lo)
    v = step * int(lo / step)
    while v <= hi:
        if v >= lo:
            out.append(f'<line x1="{left}" x2="{left + pw}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)" stroke-width="1"/>')
            out.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" text-anchor="end">{v:+.0%}</text>' if step >= 0.01 else
                       f'<text x="{left - 8}" y="{y(v) + 4:.1f}" text-anchor="end">{v:+.1%}</text>')
        v += step
    out.append(f'<line x1="{left}" x2="{left + pw}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="var(--ink2)" stroke-width="1"/>')
    # x labels: first snapshot of a day, thinned to about 8
    days = [(i, r["taken_at"][:10]) for i, r in enumerate(recs) if i == 0 or r["taken_at"][:10] != recs[i - 1]["taken_at"][:10]]
    every = max(1, len(days) // 8)
    for i, d in days[::every]:
        out.append(f'<text x="{x(i):.1f}" y="{top + ph + 18}" text-anchor="middle">{dt.date.fromisoformat(d):%b %-d}</text>')
    if not recs:
        out.append(f'<text x="{left + pw / 2}" y="{top + ph / 2}" text-anchor="middle">No snapshots yet: the first is taken '
                   'during the next trading session.</text>')
    # lines: funds first, benchmark on top
    end_labels = []
    for f in sorted(lines, key=lambda k: k in bench):
        pts = lines[f]
        d = " ".join(f"{'M' if j == 0 else 'L'}{x(i):.1f},{y(p):.1f}" for j, (i, p) in enumerate(pts))
        if f in bench:
            out.append(f'<path class="b" d="{d}"/>')
        else:
            out.append(f'<path class="l" stroke="var(--s{min(f, 9)})" d="{d}"/>')
        end_labels.append((y(pts[-1][1]), f, pts[-1][1]))
    # strategy-change markers: ringed dots on the fund's line, tagged with the fund number
    for c in changes:
        col = "var(--ink)" if c["fund"] in bench else f"var(--s{min(c['fund'], 9)})"
        cx, cy = x(c["index"]), y(c["pct"])
        out.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{cy:.1f}" y2="{top + ph}" stroke="{col}" stroke-width="1" opacity="0.5"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{col}" stroke="var(--bg)" stroke-width="2">'
                   f'<title>Fund {c["fund"]}: {escape(c["from"])} to {escape(c["to"])} ({c["taken_at"][:10]})</title></circle>')
        out.append(f'<text x="{cx:.1f}" y="{cy - 11:.1f}" text-anchor="middle" style="fill:var(--ink);font-weight:600">#{c["fund"]}</text>')
    # end labels: fund number and change, nudged apart with leader lines
    end_labels.sort()
    placed = []
    for ly, f, p in end_labels:
        ty = max(ly, placed[-1] + 14) if placed else ly
        placed.append(ty)
        x0 = x(lines[f][-1][0])
        out.append(f'<line x1="{x0 + 3:.1f}" x2="{left + pw + 8}" y1="{ly:.1f}" y2="{ty:.1f}" stroke="var(--grid)" stroke-width="1"/>')
        name = "SPY" if f in bench else f"#{f}"
        weight = ' style="font-weight:600;fill:var(--ink)"' if f in bench else ""
        out.append(f'<text x="{left + pw + 12}" y="{ty + 4:.1f}"{weight}>{name} {p:+.1%}</text>')
    # legend under the plot, four per row
    for k, f in enumerate(sorted(labels)):
        col = "var(--ink)" if f in bench else f"var(--s{min(f, 9)})"
        cx = left + (k % 4) * 205
        cy = top + ph + 46 + (k // 4) * 18
        sw = 3.5 if f in bench else 2
        out.append(f'<line x1="{cx}" x2="{cx + 16}" y1="{cy - 4}" y2="{cy - 4}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>')
        tag = " (benchmark)" if f in bench else ""
        out.append(f'<text x="{cx + 22}" y="{cy}">{f}. {escape(_plain(labels[f]))}{tag}</text>')
    k = len(labels)
    cx, cy = left + (k % 4) * 205, top + ph + 46 + (k // 4) * 18
    out.append(f'<circle cx="{cx + 8}" cy="{cy - 4}" r="5" fill="var(--ink2)" stroke="var(--bg)" stroke-width="2"/>')
    out.append(f'<text x="{cx + 22}" y="{cy}">strategy change</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _plain(label: str) -> str:
    """Drop the emoji: SVG text renders emoji inconsistently across platforms."""
    return label.split(" ", 1)[1] if " " in label else label


def _nice_step(span: float) -> float:
    for s in (0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0):
        if span / s <= 6:
            return s
    return 1.0


def changes_markdown(recs: list[dict], fund_list) -> list[str]:
    _, changes = series(recs)
    labels = {f.number: f.label for f in fund_list}
    return [f"- {c['taken_at'][:10]}: fund {c['fund']} {labels.get(c['fund'], '')} switched from `{c['from']}` to `{c['to']}`"
            for c in changes]


def main(argv=None) -> int:
    from factory import funds
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--out", required=True)
    c = sub.add_parser("chart")
    c.add_argument("--ledger", required=True)
    c.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "snapshot":
        rec = snapshot(funds.load(), _brokers())
        if rec is None:
            print("market closed or no funded account: no snapshot")
            return 0
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S}.json").write_text(json.dumps(rec, indent=2) + "\n")
        print(json.dumps(rec, indent=2))
        return 0
    Path(a.out).write_text(svg(load(Path(a.ledger)), funds.load()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
