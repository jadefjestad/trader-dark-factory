"""FRED daily market series as a look-ahead-safe macro panel (no API key needed).

FRED publishes a day's value for these series the next business day, so row t of the panel holds the
latest value dated on or before bar t-1 (one bar of lag), forward-filled across missing days.

Series: T10Y2Y (10y minus 2y Treasury), BAMLH0A0HYM2 (US high-yield option-adjusted spread),
VIXCLS (VIX close), DGS3MO (3-month Treasury yield).
"""
from __future__ import annotations

import io

import pandas as pd

from factory.data import CACHE_DIR, DataError

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES = ("T10Y2Y", "BAMLH0A0HYM2", "VIXCLS", "DGS3MO")


def fetch(series=SERIES) -> pd.DataFrame:
    import requests

    frames = []
    for sid in series:
        r = None
        for _ in range(3):
            try:
                r = requests.get(FRED_CSV_URL, params={"id": sid}, timeout=30)
                if r.status_code == 200:
                    break
            except requests.RequestException:
                continue
        if r is None or r.status_code != 200:
            raise DataError(f"FRED {sid}: {getattr(r, 'status_code', 'no response')}")
        df = pd.read_csv(io.StringIO(r.text), na_values=["."])
        df = df.rename(columns={df.columns[0]: "date"}).set_index("date")
        frames.append(pd.to_numeric(df[sid], errors="coerce"))
    out = pd.concat(frames, axis=1)
    out.index = pd.to_datetime(out.index)
    return out.sort_index()


def load(use_cache: bool = True) -> pd.DataFrame:
    """All history for SERIES, cached per UTC day so jobs without network reuse the data job's copy."""
    path = CACHE_DIR / f"macro_{pd.Timestamp.now(tz='UTC'):%Y-%m-%d}.csv.gz"
    if use_cache and path.exists():
        return pd.read_csv(path, index_col=0, parse_dates=True)
    df = fetch()
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(path)
    return df


def panel(raw: pd.DataFrame, index: pd.DatetimeIndex) -> pd.DataFrame:
    """Row t = latest value dated strictly before bar t's date (as published by bar t's close)."""
    idx = pd.DatetimeIndex(index)
    days = idx.tz_localize(None).normalize() if idx.tz is not None else idx.normalize()
    raw = raw.sort_index().ffill()
    pos = raw.index.searchsorted(days, side="left") - 1   # last observation dated before the bar's day
    vals = raw.to_numpy(dtype=float)
    out = pd.DataFrame(float("nan"), index=index, columns=list(raw.columns))
    ok = pos >= 0
    out.iloc[ok] = vals[pos[ok]]
    return out
