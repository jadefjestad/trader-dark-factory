"""Alternative data sources: reachability and history-depth probes (run in Actions, which has the keys
and the network). Nothing here feeds a strategy yet; see issues #29 (news), #30 (SEC), #31 (FRED).

    python -m factory.sources probe [--out probe.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from factory.data import _alpaca_headers

NEWS_URL = "https://data.alpaca.markets/v1beta1/news"
SEC_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
ALFRED_CSV_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv"
SEC_APP_NAME = "Trader Dark Factory"


def sec_headers() -> dict:
    """SEC requires a User-Agent naming the app and a contact email. The contact comes from the
    SEC_USER_AGENT secret only (never committed or logged); an app name is prepended if it is a bare email."""
    contact = os.environ.get("SEC_USER_AGENT", "").strip()
    if not contact:
        raise RuntimeError("SEC_USER_AGENT not set")
    ua = contact if " " in contact else f"{SEC_APP_NAME} {contact}"
    return {"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}


def _get(url, **kw):
    import requests
    return requests.get(url, timeout=30, **kw)


def probe_alpaca_news() -> dict:
    out = {}
    for label, start in (("earliest", "2015-01-01T00:00:00Z"), ("recent", "2026-09-01T00:00:00Z")):
        r = _get(NEWS_URL, headers=_alpaca_headers(),
                 params={"symbols": "AAPL,MSFT", "start": start, "limit": 50, "sort": "asc"})
        item = {"status": r.status_code}
        if r.status_code == 200:
            news = r.json().get("news") or []
            item.update(count=len(news), first=news[0]["created_at"] if news else None,
                        fields=sorted(news[0]) if news else [], source=news[0].get("source") if news else None)
        else:
            item["error"] = r.text[:200]
        out[label] = item
    return out


def probe_sec(cik: int = 320193) -> dict:
    out = {}
    r = _get(SEC_FACTS_URL.format(cik=cik), headers=sec_headers())
    out["companyfacts"] = {"status": r.status_code}
    if r.status_code == 200:
        eps = r.json().get("facts", {}).get("us-gaap", {}).get("EarningsPerShareDiluted", {}).get("units", {})
        vals = next(iter(eps.values()), [])
        out["companyfacts"].update(eps_rows=len(vals), first_filed=min((v["filed"] for v in vals), default=None),
                                   sample=vals[-1] if vals else None)
    r = _get(SEC_SUBMISSIONS_URL.format(cik=cik), headers=sec_headers())
    out["submissions"] = {"status": r.status_code}
    if r.status_code == 200:
        recent = r.json().get("filings", {}).get("recent", {})
        out["submissions"].update(filings=len(recent.get("form", [])),
                                  has_acceptance_time="acceptanceDateTime" in recent,
                                  sample_acceptance=(recent.get("acceptanceDateTime") or [None])[0])
    return out


def probe_fred() -> dict:
    out = {}
    for name, url, params in (("fred_T10Y2Y", FRED_CSV_URL, {"id": "T10Y2Y"}),
                              ("alfred_UNRATE_vintages", ALFRED_CSV_URL, {"id": "UNRATE", "vintage_date": "2020-06-01"})):
        r = _get(url, params=params)
        lines = r.text.strip().splitlines() if r.status_code == 200 else []
        out[name] = {"status": r.status_code, "rows": max(len(lines) - 1, 0),
                     "header": lines[0] if lines else None, "last": lines[-1] if lines else None}
    return out


def probe() -> dict:
    res = {}
    for name, fn in (("alpaca_news", probe_alpaca_news), ("sec_edgar", probe_sec), ("fred", probe_fred)):
        try:
            res[name] = fn()
        except Exception as e:  # a probe reports, it never fails the job
            res[name] = {"error": f"{type(e).__name__}: {e}"[:300]}
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe"])
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    text = json.dumps(probe(), indent=2, default=str)
    print(text)
    if a.out:
        open(a.out, "w").write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
