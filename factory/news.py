"""Alpaca news (Benzinga) for the universe: download, yearly cache, and a look-ahead-safe daily panel.

An article counts toward daily bar d when it was created at or before 16:00 New York time on d; later
articles roll to the next bar. `created_at` is used, never `updated_at`, so revisions cannot leak.
Fetch failures raise DataError, so a strategy that needs news places no orders without it.

    python -m factory.news backfill --start 2015 --end 2026
"""
from __future__ import annotations

import argparse
import sys
import time

import pandas as pd

from factory.data import CACHE_DIR, DataError, _alpaca_headers

NEWS_URL = "https://data.alpaca.markets/v1beta1/news"
CLOSE = pd.Timedelta(hours=16)
COLUMNS = ["id", "created_at", "symbols", "headline"]


def fetch(symbols: list[str], start: str, end: str, pause: float = 0.31) -> pd.DataFrame:
    """All articles tagged with any of `symbols` between start and end (RFC3339 or YYYY-MM-DD)."""
    import requests

    params = {"symbols": ",".join(symbols), "start": start, "end": end, "limit": 50, "sort": "asc",
              "include_content": "false"}
    headers, rows = _alpaca_headers(), []
    for page in range(100000):
        for attempt in range(6):
            r = requests.get(NEWS_URL, params=params, headers=headers, timeout=30)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** attempt * 2)
                continue
            break
        if r.status_code != 200:
            raise DataError(f"alpaca news {r.status_code}: {r.text[:200]}")
        body = r.json()
        for a in body.get("news") or []:
            rows.append((a["id"], a["created_at"], "|".join(a.get("symbols") or []), a.get("headline") or ""))
        token = body.get("next_page_token")
        if not token:
            break
        params["page_token"] = token
        if page and page % 200 == 0:
            print(f"  news {start[:10]}: {page} pages, {len(rows):,} articles", file=sys.stderr, flush=True)
        time.sleep(pause)
    return pd.DataFrame(rows, columns=COLUMNS).drop_duplicates("id")


def _year_path(year: int):
    return CACHE_DIR / f"news_{year}.csv.gz"


def load(symbols: list[str], start: str, end: str = "latest", use_cache: bool = True) -> pd.DataFrame:
    """Articles from `start` to `end`. Complete past years are cached on disk; the current year is fetched."""
    now = pd.Timestamp.now(tz="UTC")
    end_ts = now if end == "latest" else pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
    frames = []
    for year in range(pd.Timestamp(start).year, end_ts.year + 1):
        complete = year < now.year
        # the running year is cached per day so a job without keys can reuse what the data job fetched
        path = _year_path(year) if complete else CACHE_DIR / f"news_{year}_to_{(end_ts - pd.Timedelta(days=1) if end != 'latest' else now):%Y-%m-%d}.csv.gz"
        if use_cache and path.exists():
            frames.append(pd.read_csv(path, keep_default_na=False))
            continue
        lo = f"{year}-01-01T00:00:00Z"
        hi = f"{year + 1}-01-01T00:00:00Z" if complete else end_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        df = fetch(symbols, lo, hi)
        if use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=COLUMNS)
    t = pd.to_datetime(out["created_at"], utc=True)
    return out[(t >= pd.Timestamp(start, tz="UTC")) & (t < end_ts)].reset_index(drop=True)


def bar_dates(created_at: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Map article times to the first daily bar whose 16:00 New York close is at or after them (NaT if none)."""
    et = pd.to_datetime(created_at, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    day = et.dt.normalize()
    day = day.where(et - day <= CLOSE, day + pd.Timedelta(days=1))
    idx = pd.DatetimeIndex(index)
    pos = idx.searchsorted(day.values, side="left")
    ok = pos < len(idx)
    out = pd.Series(pd.NaT, index=created_at.index, dtype="datetime64[ns]")
    out[ok] = idx[pos[ok]]
    return out


def count_panel(articles: pd.DataFrame, index: pd.DatetimeIndex, symbols: list[str]) -> pd.DataFrame:
    """Articles per symbol per daily bar (0 when none)."""
    panel = pd.DataFrame(0.0, index=index, columns=symbols)
    if articles.empty:
        return panel
    d = articles.assign(bar=bar_dates(articles["created_at"], index), symbol=articles["symbols"].str.split("|"))
    d = d.dropna(subset=["bar"]).explode("symbol")
    d = d[d["symbol"].isin(symbols)]
    counts = d.groupby(["bar", "symbol"]).size().unstack(fill_value=0)
    panel.loc[:, :] = counts.reindex(index=index, columns=symbols, fill_value=0).to_numpy(dtype=float)
    return panel


def main(argv=None) -> int:
    from factory import config

    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["backfill"])
    ap.add_argument("--start", type=int, default=2015)
    ap.add_argument("--end", type=int, default=pd.Timestamp.now().year - 1)
    a = ap.parse_args(argv)
    symbols = config.universe()["symbols"]
    for year in range(a.start, a.end + 1):
        t0 = time.time()
        df = load(symbols, f"{year}-01-01", f"{year}-12-31")
        print(f"::notice title=news {year}::{len(df)} articles in {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------- headline sentiment
# A small fixed finance lexicon (in the spirit of Loughran-McDonald), applied deterministically to headlines.
POSITIVE = frozenset("""
beat beats beating tops topped exceeds exceeded surpass surpasses upgrade upgrades upgraded raise raises raised
boost boosts boosted record strong stronger strength surge surges surged soar soars soared jump jumps jumped
rally rallies rallied gain gains gained growth grows outperform outperforms bullish buy approval approved
approves win wins won expands expansion profit profitable rebound rebounds rebounded higher upbeat optimistic
breakthrough partnership accelerates accelerating tailwind tailwinds overweight
""".split())
NEGATIVE = frozenset("""
miss misses missed downgrade downgrades downgraded cut cuts cutting lower lowers lowered weak weaker weakness
plunge plunges plunged drop drops dropped fall falls fell slump slumps slumped sink sinks sank tumble tumbles
tumbled decline declines declined loss losses lawsuit lawsuits sue sued sues probe investigation investigates
recall recalls fine fined penalty layoffs layoff warns warning bearish sell underperform underperforms
underweight halt halts halted delay delays delayed concern concerns risk risks headwind headwinds fraud
antitrust subpoena bankruptcy default disappointing disappoints slowdown
""".split())
_WORD = __import__("re").compile(r"[a-z]+")


def headline_score(text: str) -> float:
    """(positive - negative) word count of a headline, clipped to [-2, 2]."""
    words = _WORD.findall(str(text).lower())
    s = sum(w in POSITIVE for w in words) - sum(w in NEGATIVE for w in words)
    return float(max(-2, min(2, s)))


def sentiment_panel(articles: pd.DataFrame, index: pd.DatetimeIndex, symbols: list[str]) -> pd.DataFrame:
    """Sum of headline scores per symbol per daily bar (0 when no news), same timing rule as count_panel."""
    panel = pd.DataFrame(0.0, index=index, columns=symbols)
    if articles.empty:
        return panel
    d = articles.assign(bar=bar_dates(articles["created_at"], index), symbol=articles["symbols"].str.split("|"),
                        score=articles["headline"].map(headline_score))
    d = d.dropna(subset=["bar"]).explode("symbol")
    d = d[d["symbol"].isin(symbols)]
    sums = d.groupby(["bar", "symbol"])["score"].sum().unstack(fill_value=0.0)
    panel.loc[:, :] = sums.reindex(index=index, columns=symbols, fill_value=0.0).to_numpy(dtype=float)
    return panel
