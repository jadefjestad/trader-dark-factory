"""FINRA short-sale data (issue #65): daily Reg SHO short volume and twice-monthly short interest.

Both are free and keyless. The session network blocks FINRA, so `probe` runs in Actions
(.github/workflows/probe.yml) and reports what each source returns.

Availability rules (no look-ahead):
- A daily short-volume file for trade date D is published that evening, so it is usable from the
  first bar after D: on daily bars, row D+1 onwards.
- Short interest for a settlement date is published about 7 business days later; it is usable only
  from the first bar after its publication date, never from the settlement date.

    python -m factory.shorts probe [--out shorts_probe.json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys

import pandas as pd

DAILY_URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{day:%Y%m%d}.txt"
SHORT_INTEREST_URL = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
PUBLICATION_LAG_BDAYS = 7    # conservative when a record carries no publication date


def _get(url, **kw):
    import requests
    return requests.get(url, timeout=30, **kw)


def _post(url, **kw):
    import requests
    return requests.post(url, timeout=30, **kw)


def parse_daily(text: str) -> pd.DataFrame:
    """One CNMSshvol file -> rows (date, symbol, short_volume, total_volume). Pure; unit-tested offline."""
    body = "\n".join(x for x in text.splitlines() if x.count("|") >= 4)   # drops the record-count trailer
    df = pd.read_csv(io.StringIO(body), sep="|", dtype={"Date": str, "Symbol": str})
    out = pd.DataFrame({"date": pd.to_datetime(df["Date"], format="%Y%m%d"), "symbol": df["Symbol"],
                        "short_volume": df["ShortVolume"].astype(float),
                        "total_volume": df["TotalVolume"].astype(float)})
    return out[out["total_volume"] > 0].reset_index(drop=True)


def available_from(dates: pd.Series, lag_bdays: int = 0) -> pd.Series:
    """First calendar day a record dated `dates` may be used: the business day after date + lag."""
    return pd.to_datetime(dates) + pd.offsets.BDay(lag_bdays + 1)


def short_volume_ratio_panel(rows: pd.DataFrame, index: pd.DatetimeIndex, symbols: list[str]) -> pd.DataFrame:
    """Daily-bar panel of short volume / total volume; row t holds the latest file published before bar t."""
    rows = rows[rows["symbol"].isin(symbols)].assign(usable=lambda d: available_from(d["date"]))
    rows = rows.assign(ratio=rows["short_volume"] / rows["total_volume"])
    wide = rows.pivot_table(index="usable", columns="symbol", values="ratio", aggfunc="last").sort_index()
    return wide.reindex(columns=symbols).reindex(index.union(wide.index)).ffill().reindex(index)


def probe_daily(day: dt.date) -> dict:
    out = {}
    for d in (day, dt.date(2010, 8, 2), dt.date(2018, 8, 1)):   # recent, and how far history goes
        r = _get(DAILY_URL.format(day=d))
        entry = {"status": r.status_code}
        if r.status_code == 200:
            rows = parse_daily(r.text)
            aapl = rows[rows["symbol"] == "AAPL"]
            entry.update(symbols=int(rows["symbol"].nunique()),
                         aapl_ratio=round(float(aapl["short_volume"].iloc[0] / aapl["total_volume"].iloc[0]), 3)
                         if len(aapl) else None)
        out[str(d)] = entry
    return out


def probe_short_interest() -> dict:
    body = {"limit": 3, "compareFilters": [{"compareType": "equal", "fieldName": "symbolCode", "fieldValue": "AAPL"}],
            "sortFields": ["-settlementDate"]}
    r = _post(SHORT_INTEREST_URL, json=body, headers={"Accept": "application/json"})
    out = {"status": r.status_code}
    if r.status_code == 200:
        recs = r.json() if r.text.strip() else []
        out.update(records=len(recs), fields=sorted(recs[0]) if recs else [], sample=recs[0] if recs else None)
    else:
        out["body"] = r.text[:200]
    r = _post(SHORT_INTEREST_URL, json={**body, "sortFields": ["settlementDate"], "limit": 1},
              headers={"Accept": "application/json"})
    if r.status_code == 200 and r.text.strip():
        recs = r.json()
        out["earliest_settlement"] = recs[0].get("settlementDate") if recs else None
    return out


def last_weekday(today: dt.date) -> dt.date:
    d = today - dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def probe() -> dict:
    res = {}
    for name, fn in (("regsho_daily", lambda: probe_daily(last_weekday(dt.date.today()))),
                     ("short_interest", probe_short_interest)):
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
