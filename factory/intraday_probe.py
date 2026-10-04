"""What the free Alpaca plan can support intraday (issue #67). Run in Actions, which has the keys and network.

Measures, for the universe on recent full sessions:
- IEX share of consolidated (SIP) volume, and how many of the 390 regular-session minutes have an IEX bar;
- how far IEX minute closes sit from SIP minute closes (bps), i.e. the error of signalling on IEX;
- IEX quoted spreads from the latest quotes;
- whether SIP bars from the last 15 minutes are refused on the free plan, and how far back 1-minute history goes;
- Tiingo and Twelve Data free tiers, only when their keys are present (otherwise reported as not configured).

    python -m factory.intraday_probe [--days 3] [--out intraday_probe.json]

It only reads data; it never places orders. Results are summaries, not the raw bars.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import statistics
import sys

import pandas as pd

from factory import config
from factory.data import DATA_URL, _alpaca_headers

QUOTES_URL = "https://data.alpaca.markets/v2/stocks/quotes/latest"
TIINGO_URL = "https://api.tiingo.com/iex/{sym}/prices"
TWELVEDATA_URL = "https://api.twelvedata.com/time_series"
SESSION_MINUTES = 390


def _get(url, **kw):
    import requests
    return requests.get(url, timeout=30, **kw)


def _minute_bars(symbols, start, end, feed) -> pd.DataFrame:
    """1-minute bars as a long frame (symbol, t, c, v); raises on a non-200 answer."""
    rows, params = [], {"symbols": ",".join(symbols), "timeframe": "1Min", "start": start, "end": end,
                        "feed": feed, "limit": 10000, "sort": "asc"}
    for _ in range(200):
        r = _get(DATA_URL, params=params, headers=_alpaca_headers())
        if r.status_code != 200:
            raise RuntimeError(f"{feed} bars {r.status_code}: {r.text[:150]}")
        body = r.json()
        for sym, bars in (body.get("bars") or {}).items():
            rows += [(sym, b["t"], b["c"], b["v"]) for b in bars]
        if not body.get("next_page_token"):
            break
        params["page_token"] = body["next_page_token"]
    df = pd.DataFrame(rows, columns=["symbol", "t", "c", "v"])
    df["t"] = pd.to_datetime(df["t"], utc=True).dt.tz_convert("America/New_York")
    return df[(df["t"].dt.time >= dt.time(9, 30)) & (df["t"].dt.time < dt.time(16, 0))]


def compare_minute_bars(iex: pd.DataFrame, sip: pd.DataFrame, sessions: int) -> dict:
    """Per-symbol IEX vs SIP comparison, summarised across the universe. Pure; unit-tested offline."""
    per = {}
    for sym, s in sip.groupby("symbol"):
        i = iex[iex["symbol"] == sym]
        joined = s.merge(i, on="t", suffixes=("_sip", "_iex"))
        gap = ((joined["c_iex"] / joined["c_sip"] - 1).abs() * 1e4) if len(joined) else pd.Series(dtype=float)
        per[sym] = {
            "iex_volume_share": float(i["v"].sum() / s["v"].sum()) if s["v"].sum() else None,
            "iex_minute_coverage": len(i) / (SESSION_MINUTES * sessions),
            "close_gap_bps_median": float(gap.median()) if len(gap) else None,
            "close_gap_bps_p95": float(gap.quantile(0.95)) if len(gap) else None,
        }

    def summ(key):
        vals = [v[key] for v in per.values() if v[key] is not None]
        return {"median": round(statistics.median(vals), 4), "min": round(min(vals), 4),
                "max": round(max(vals), 4)} if vals else None

    return {"symbols": len(per), "sessions": sessions,
            **{k: summ(k) for k in ("iex_volume_share", "iex_minute_coverage",
                                    "close_gap_bps_median", "close_gap_bps_p95")}}


def recent_sessions(today: dt.date, n: int) -> list[dt.date]:
    """The n most recent weekdays strictly before today (holidays just yield fewer bars)."""
    out, d = [], today
    while len(out) < n:
        d -= dt.timedelta(days=1)
        if d.weekday() < 5:
            out.append(d)
    return sorted(out)


def probe_feeds(symbols, days) -> dict:
    sessions = recent_sessions(dt.date.today(), days)
    start, end = f"{sessions[0]}T13:00:00Z", f"{sessions[-1]}T21:00:00Z"
    iex, sip = _minute_bars(symbols, start, end, "iex"), _minute_bars(symbols, start, end, "sip")
    n = max(sip["t"].dt.date.nunique(), 1)
    return {"window": [str(sessions[0]), str(sessions[-1])], **compare_minute_bars(iex, sip, n)}


def probe_spreads(symbols) -> dict:
    r = _get(QUOTES_URL, params={"symbols": ",".join(symbols), "feed": "iex"}, headers=_alpaca_headers())
    if r.status_code != 200:
        return {"status": r.status_code, "error": r.text[:150]}
    bps = []
    for q in (r.json().get("quotes") or {}).values():
        bid, ask = q.get("bp") or 0, q.get("ap") or 0
        if bid > 0 and ask >= bid:
            bps.append((ask - bid) / ((ask + bid) / 2) * 1e4)
    return {"status": 200, "quotes": len(bps),
            "spread_bps_median": round(statistics.median(bps), 2) if bps else None,
            "note": "latest IEX quote; outside market hours spreads are wider than intraday"}


def probe_limits() -> dict:
    now = dt.datetime.now(dt.timezone.utc)
    out = {}
    r = _get(DATA_URL, headers=_alpaca_headers(), params={
        "symbols": "AAPL", "timeframe": "1Min", "feed": "sip", "limit": 5,
        "start": (now - dt.timedelta(minutes=10)).isoformat(timespec="seconds").replace("+00:00", "Z")})
    out["sip_last_15min"] = {"status": r.status_code, "body": r.text[:120]}
    r = _get(DATA_URL, headers=_alpaca_headers(), params={
        "symbols": "AAPL", "timeframe": "1Min", "feed": "sip", "limit": 1, "start": "2015-01-01T00:00:00Z"})
    bars = (r.json().get("bars") or {}).get("AAPL") if r.status_code == 200 else None
    out["sip_1min_earliest"] = bars[0]["t"] if bars else {"status": r.status_code}
    r = _get(DATA_URL, headers=_alpaca_headers(), params={
        "symbols": "AAPL", "timeframe": "1Min", "feed": "iex", "limit": 1, "start": "2015-01-01T00:00:00Z"})
    bars = (r.json().get("bars") or {}).get("AAPL") if r.status_code == 200 else None
    out["iex_1min_earliest"] = bars[0]["t"] if bars else {"status": r.status_code}
    out["rate_limit_header"] = r.headers.get("X-RateLimit-Limit")
    return out


def probe_third_party(day: dt.date) -> dict:
    """Tiingo and Twelve Data free tiers, only if their keys are configured as secrets."""
    out = {}
    key = os.environ.get("TIINGO_API_KEY")
    if not key:
        out["tiingo"] = "not configured (TIINGO_API_KEY)"
    else:
        r = _get(TIINGO_URL.format(sym="aapl"), params={"startDate": str(day), "endDate": str(day),
                                                        "resampleFreq": "1min", "token": key})
        rows = r.json() if r.status_code == 200 else []
        out["tiingo"] = {"status": r.status_code, "minutes": len(rows), "first": rows[0] if rows else r.text[:120]}
    key = os.environ.get("TWELVEDATA_API_KEY")
    if not key:
        out["twelvedata"] = "not configured (TWELVEDATA_API_KEY)"
    else:
        r = _get(TWELVEDATA_URL, params={"symbol": "AAPL", "interval": "1min", "date": str(day),
                                         "outputsize": 5000, "apikey": key})
        body = r.json() if r.status_code == 200 else {}
        out["twelvedata"] = {"status": r.status_code, "minutes": len(body.get("values") or []),
                             "meta": body.get("meta") or body.get("message") or r.text[:120]}
    return out


def probe(days: int = 3) -> dict:
    symbols = config.universe()["symbols"]
    res = {}
    for name, fn in (("feeds", lambda: probe_feeds(symbols, days)), ("spreads", lambda: probe_spreads(symbols)),
                     ("limits", probe_limits),
                     ("third_party", lambda: probe_third_party(recent_sessions(dt.date.today(), 1)[0]))):
        try:
            res[name] = fn()
        except Exception as e:  # a probe reports, it never fails the job
            res[name] = {"error": f"{type(e).__name__}: {e}"[:300]}
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    text = json.dumps(probe(a.days), indent=2, default=str)
    print(text)
    if a.out:
        open(a.out, "w").write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
