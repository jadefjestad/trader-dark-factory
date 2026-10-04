"""SEC EDGAR access shared by the fundamentals (#30), insider (#64) and earnings (#66) panels.

Every request sends the SEC_USER_AGENT contact (factory.sources.sec_headers) and stays under SEC's
10 requests/second fair-access limit. Downloads are cached under data/cache per UTC day, so the
evaluate job (no network, no secrets) reuses what the data job fetched. Failures raise DataError: a
strategy that needs SEC data places no orders without it.

Availability rule (no look-ahead): a filing counts toward daily bar d when EDGAR accepted it at or
before 16:00 New York time on d; later filings roll to the next bar. EDGAR's `acceptanceDateTime` is
UTC (the probe shows Apple's 4:30 pm ET releases at 20:30Z in summer and 21:30Z in winter). A filing
without an acceptance time falls back to the first bar after its filing date.

Some tickers changed registrant (Google Inc became Alphabet, Avago became Broadcom, Exxon Mobil moved
to a new holding company in 2026), so a symbol maps to its current CIK plus PREDECESSORS.
"""
from __future__ import annotations

import gzip
import io
import json
import time

import numpy as np
import pandas as pd

from factory.data import CACHE_DIR, DataError

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SUBMISSIONS_PAGE_URL = "https://data.sec.gov/submissions/{name}"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}"
CLOSE = pd.Timedelta(hours=16)
MIN_INTERVAL = 0.125            # seconds between requests: 8/s, under SEC's 10/s limit
FILINGS_SINCE = "2014-01-01"    # older submission pages are skipped (evaluation warm-up starts 2015)
FILING_COLUMNS = ["accessionNumber", "form", "filingDate", "acceptanceDateTime", "items", "primaryDocument"]

_last_request = [0.0]


def get(url: str, missing_ok: bool = False) -> bytes | None:
    """GET with the SEC contact header, pacing and retries. None for a 404 when missing_ok."""
    import requests

    from factory.sources import sec_headers

    try:
        headers = sec_headers()
    except RuntimeError as e:
        raise DataError(str(e)) from None
    r = None
    for attempt in range(6):
        wait = _last_request[0] + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()
        try:
            r = requests.get(url, headers=headers, timeout=60)
        except requests.RequestException:
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** attempt * 2)
            continue
        break
    if r is not None and r.status_code == 404 and missing_ok:
        return None
    if r is None or r.status_code != 200:
        # the URL is safe to report; the contact header never is
        raise DataError(f"SEC {url}: {getattr(r, 'status_code', 'no response')}")
    return r.content


def get_json(url: str) -> dict:
    return json.loads(get(url))


def _today() -> str:
    return f"{pd.Timestamp.now(tz='UTC'):%Y-%m-%d}"


def daily_cache(name: str):
    """Path of today's cached table `name` (one file per UTC day, like the news and macro caches)."""
    return CACHE_DIR / f"sec_{name}_{_today()}.csv.gz"


def cached_table(name: str, build, use_cache: bool = True) -> pd.DataFrame:
    path = daily_cache(name)
    if use_cache and path.exists():
        return pd.read_csv(path, keep_default_na=False, na_values=[""], dtype={"items": str, "accessionNumber": str})
    df = build()
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    return df


def cik_map(symbols: list[str], use_cache: bool = True) -> dict[str, int]:
    """Ticker -> CIK from SEC's company_tickers.json. A ticker SEC does not list is an error."""
    def build():
        rows = get_json(TICKERS_URL).values()
        return pd.DataFrame([(r["ticker"].upper(), int(r["cik_str"])) for r in rows], columns=["ticker", "cik"])

    t = cached_table("tickers", build, use_cache)
    m = dict(zip(t["ticker"].astype(str), t["cik"].astype(int)))
    missing = [s for s in symbols if s.upper() not in m]
    if missing:
        raise DataError(f"no SEC CIK for {missing}")
    return {s: m[s.upper()] for s in symbols}


# earlier registrants whose filings belong to today's ticker (checked by factory.sec_probe)
PREDECESSORS = {
    "GOOGL": [1288776],            # Google Inc., before Alphabet (October 2015)
    "AVGO": [1649338, 1441634],    # Broadcom Ltd (2016-2018) and Avago Technologies (to 2016)
    "XOM": [34088],                # Exxon Mobil Corp, before the 2026 holding-company reorganization
}


def ciks_for(symbols: list[str], use_cache: bool = True) -> dict[str, list[int]]:
    """Symbol -> [current CIK, predecessor CIKs...]."""
    cur = cik_map(symbols, use_cache)
    return {s: [cur[s]] + [c for c in PREDECESSORS.get(s.upper(), []) if c != cur[s]] for s in symbols}


def _page_rows(block: dict) -> pd.DataFrame:
    n = len(block.get("accessionNumber", []))
    return pd.DataFrame({c: block.get(c, [""] * n) for c in FILING_COLUMNS})


def fetch_filings(cik: int, since: str = FILINGS_SINCE) -> pd.DataFrame:
    """Every filing index row for `cik` filed on or after `since` (recent block plus older pages)."""
    sub = get_json(SUBMISSIONS_URL.format(cik=cik))
    frames = [_page_rows(sub.get("filings", {}).get("recent", {}))]
    for f in sub.get("filings", {}).get("files", []):
        if f.get("filingTo", "9999") < since:
            continue
        frames.append(_page_rows(get_json(SUBMISSIONS_PAGE_URL.format(name=f["name"]))))
    df = pd.concat(frames, ignore_index=True).drop_duplicates("accessionNumber")
    return df[df["filingDate"] >= since].reset_index(drop=True)


FORMS_KEPT = ("10-K", "10-Q", "10-K/A", "10-Q/A", "8-K", "4", "20-F", "40-F", "6-K")


def filings(symbols: list[str], use_cache: bool = True) -> pd.DataFrame:
    """Filing index for the universe (forms the panels use), with a `symbol` column."""
    def build():
        frames = []
        for s, ciks in ciks_for(symbols, use_cache).items():
            for cik in ciks:
                df = fetch_filings(cik)
                frames.append(df[df["form"].isin(FORMS_KEPT)].assign(symbol=s, cik=cik))
        return pd.concat(frames, ignore_index=True).drop_duplicates("accessionNumber")

    return cached_table("filings", build, use_cache)


def acceptance_times(accepted: pd.Series) -> pd.Series:
    """EDGAR acceptanceDateTime strings (UTC) as naive New York times."""
    t = pd.to_datetime(accepted.fillna("").astype(str), utc=True, errors="coerce", format="ISO8601")
    return t.dt.tz_convert("America/New_York").dt.tz_localize(None)


def available_bar(accepted_et: pd.Series, filed: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """First daily bar at whose 16:00 New York close the filing was public (NaT if after the last bar).

    Uses the acceptance time when present, else the first bar strictly after the filing date."""
    idx = pd.DatetimeIndex(index)
    idx = idx.tz_localize(None) if idx.tz is not None else idx
    t = pd.to_datetime(accepted_et)
    day = t.dt.normalize()
    day = day.where(t - day <= CLOSE, day + pd.Timedelta(days=1))
    fallback = pd.to_datetime(filed, errors="coerce").dt.normalize() + pd.Timedelta(days=1)
    day = day.where(t.notna(), fallback)
    pos = idx.searchsorted(day.values, side="left")
    ok = (pos < len(idx)) & day.notna().to_numpy()
    out = pd.Series(pd.NaT, index=accepted_et.index, dtype="datetime64[ns]")
    out[ok] = idx[pos[ok]]
    return out


def gz_json(data: bytes) -> dict:
    """Decode a JSON body that may still be gzip-compressed."""
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return json.loads(data)


def read_zip_member(data: bytes, member: str) -> pd.DataFrame:
    import zipfile

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name = next((n for n in z.namelist() if n.upper().endswith(member.upper())), None)
        if name is None:
            raise DataError(f"{member} missing from SEC archive")
        with z.open(name) as f:
            return pd.read_csv(f, sep="\t", dtype=str, keep_default_na=False, quoting=3)


def stamp(events: pd.DataFrame, index: pd.DatetimeIndex, symbols: list[str], value: str,
          how: str = "last") -> pd.DataFrame:
    """Panel with each event's `value` placed on its `bar` (combined with `how` when several share a bar)."""
    panel = pd.DataFrame(np.nan, index=index, columns=symbols)
    ev = events.dropna(subset=["bar", value])
    ev = ev[ev["symbol"].isin(symbols)]
    if ev.empty:
        return panel
    g = ev.groupby(["bar", "symbol"])[value].agg(how).unstack()
    g = g.reindex(index=pd.DatetimeIndex(index), columns=symbols)
    return pd.DataFrame(g.to_numpy(dtype=float), index=index, columns=symbols)
