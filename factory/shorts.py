"""FINRA short-sale data (issue #65): daily Reg SHO short volume and twice-monthly short interest.

Both are free and keyless. The session network blocks FINRA, so `probe` runs in Actions
(.github/workflows/probe.yml) and reports what each source returns.

Availability rules (no look-ahead):
- A daily short-volume file for trade date D is published that evening, so it is usable from the
  first bar after D: on daily bars, row D+1 onwards.
- Short interest for a settlement date is published about 7 business days later; it is usable only
  from the first bar after its publication date, never from the settlement date.

    python -m factory.shorts probe [--out shorts_probe.json]
    python -m factory.shorts backfill --start 2018 [--end 2025]   # cache complete years (Actions)
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import sys
import time

import pandas as pd

from factory.data import CACHE_DIR, DataError

DAILY_URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{day:%Y%m%d}.txt"
SHORT_INTEREST_URL = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
PUBLICATION_LAG_BDAYS = 7    # conservative when a record carries no publication date
FIRST_YEAR = 2018            # older daily files answer 403 from Actions (probe, 2026-10-04)
MAX_MISSING_DAYS = 0.06      # holidays have no file (~4%); more missing than this means a broken download
COLUMNS = ["date", "symbol", "short_volume", "total_volume"]


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


def fetch_days(days, symbols: list[str], pause: float = 0.2) -> pd.DataFrame:
    """Download and parse the daily files for `days`, keeping `symbols`. Raises DataError if too many are missing."""
    frames, missing = [], []
    for d in days:
        r = None
        for attempt in range(4):
            try:
                r = _get(DAILY_URL.format(day=d))
            except Exception:  # network blip: retry, then count the day as missing
                r = None
            if r is not None and r.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(2 ** attempt)
        if r is None or r.status_code != 200:
            missing.append(str(d))
            continue
        rows = parse_daily(r.text)
        frames.append(rows[rows["symbol"].isin(symbols)])
        time.sleep(pause)
    if days and len(missing) / len(days) > MAX_MISSING_DAYS:
        raise DataError(f"FINRA short volume: {len(missing)} of {len(days)} days missing, e.g. {missing[:5]}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)


def _year_path(year: int):
    return CACHE_DIR / f"shorts_{year}.csv.gz"


def load(symbols: list[str], start: str, end: str = "latest", use_cache: bool = True) -> pd.DataFrame:
    """Daily short volume rows from `start` to `end`. Complete years are cached; the running year is cached per day."""
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    end_ts = today if end == "latest" else pd.Timestamp(end)
    frames = []
    for year in range(max(pd.Timestamp(start).year, FIRST_YEAR), end_ts.year + 1):
        complete = year < today.year
        last = pd.Timestamp(f"{year}-12-31") if complete else min(end_ts, today - pd.Timedelta(days=1))
        path = _year_path(year) if complete else CACHE_DIR / f"shorts_{year}_to_{last:%Y-%m-%d}.csv.gz"
        if use_cache and path.exists():
            frames.append(pd.read_csv(path, parse_dates=["date"]))
            continue
        days = [d.date() for d in pd.bdate_range(f"{year}-01-01", last)]
        df = fetch_days(days, symbols)
        if use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)
    out["date"] = pd.to_datetime(out["date"])
    return out[(out["date"] >= pd.Timestamp(start)) & (out["date"] <= end_ts)].reset_index(drop=True)


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
    # the API refuses sorting unless every partition key is filtered, so fetch AAPL's records and sort here
    body = {"limit": 5000, "compareFilters": [{"compareType": "equal", "fieldName": "symbolCode", "fieldValue": "AAPL"}]}
    r = _post(SHORT_INTEREST_URL, json=body, headers={"Accept": "application/json"})
    out = {"status": r.status_code}
    if r.status_code == 200:
        recs = r.json() if r.text.strip() else []
        dates = sorted(x.get("settlementDate") for x in recs if x.get("settlementDate"))
        out.update(records=len(recs), fields=sorted(recs[0]) if recs else [],
                   earliest_settlement=dates[0] if dates else None, latest_settlement=dates[-1] if dates else None,
                   sample=max(recs, key=lambda x: x.get("settlementDate") or "") if recs else None)
    else:
        out["body"] = r.text[:200]
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
    ap.add_argument("cmd", choices=["probe", "backfill"])
    ap.add_argument("--out")
    ap.add_argument("--start", type=int, default=FIRST_YEAR)
    ap.add_argument("--end", type=int, default=dt.date.today().year - 1)
    a = ap.parse_args(argv)
    if a.cmd == "backfill":
        from factory import config
        u = config.universe()
        for year in range(a.start, a.end + 1):
            t0 = time.time()
            df = load(u["symbols"] + [u["benchmark"]], f"{year}-01-01", f"{year}-12-31")
            print(f"::notice title=shorts {year}::{len(df)} rows in {time.time() - t0:.0f}s", flush=True)
        return 0
    text = json.dumps(probe(), indent=2, default=str)
    print(text)
    if a.out:
        open(a.out, "w").write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
