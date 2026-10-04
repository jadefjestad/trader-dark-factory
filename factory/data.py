"""Market data: Alpaca historical bars, a local cache, validation, and a synthetic generator for tests.

Every loader returns a MarketData whose frames are wide (index = bar time, columns = symbols).
Validation failures raise DataError; callers that trade must treat that as "place no orders".
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from factory.config import ROOT

DATA_URL = "https://data.alpaca.markets/v2/stocks/bars"
CACHE_DIR = Path(os.environ.get("FACTORY_DATA_CACHE", ROOT / "data" / "cache"))
FIELDS = ("open", "high", "low", "close", "volume")


class DataError(RuntimeError):
    pass


@dataclass
class MarketData:
    open: pd.DataFrame
    high: pd.DataFrame
    low: pd.DataFrame
    close: pd.DataFrame
    volume: pd.DataFrame
    timeframe: str = "1Day"
    source: str = "unknown"

    @property
    def index(self) -> pd.Index:
        return self.close.index

    @property
    def symbols(self) -> list[str]:
        return list(self.close.columns)

    def slice(self, start=None, end=None) -> "MarketData":
        def s(df):
            return df.loc[start:end]
        return MarketData(*(s(getattr(self, f)) for f in FIELDS), timeframe=self.timeframe, source=self.source)

    def head(self, n: int) -> "MarketData":
        return MarketData(*(getattr(self, f).iloc[:n] for f in FIELDS), timeframe=self.timeframe, source=self.source)

    def select(self, symbols: list[str]) -> "MarketData":
        return MarketData(*(getattr(self, f)[symbols] for f in FIELDS), timeframe=self.timeframe, source=self.source)

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(self.source.encode())
        h.update(pd.util.hash_pandas_object(self.close, index=True).values.tobytes())
        return h.hexdigest()[:16]


def validate(md: MarketData, symbols: list[str], max_missing_frac: float = 0.02) -> None:
    """Raise DataError if the data cannot be trusted."""
    missing = [s for s in symbols if s not in md.close.columns]
    if missing:
        raise DataError(f"missing symbols: {missing}")
    if len(md.index) < 2:
        raise DataError("fewer than two bars")
    if not md.index.is_monotonic_increasing or md.index.has_duplicates:
        raise DataError("bar index not strictly increasing")
    for f in ("open", "high", "low", "close"):
        df = getattr(md, f)[symbols]
        if (df <= 0).any().any():
            raise DataError(f"non-positive {f} prices")
        frac = df.isna().mean()
        bad = frac[frac > max_missing_frac]
        if len(bad):
            raise DataError(f"too many missing {f} values: {bad.round(3).to_dict()}")
    if (md.high[symbols] < md.low[symbols]).any().any():
        raise DataError("high below low")


# ---------------------------------------------------------------- Alpaca

def _alpaca_headers() -> dict:
    key = os.environ.get("ALPACA_API_KEY_ID")
    secret = os.environ.get("ALPACA_API_SECRET_KEY")
    if not key or not secret:
        raise DataError("ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY not set")
    return {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}


def _fetch_alpaca(symbols, start, end, timeframe, feed, adjustment) -> pd.DataFrame:
    import requests

    rows = []
    params = {
        "symbols": ",".join(symbols), "timeframe": timeframe, "start": start, "end": end,
        "adjustment": adjustment, "feed": feed, "limit": 10000, "sort": "asc",
    }
    headers = _alpaca_headers()
    for _ in range(10000):
        for attempt in range(5):
            r = requests.get(DATA_URL, params=params, headers=headers, timeout=30)
            if r.status_code == 429:  # free plan: 200 requests/minute
                time.sleep(2 ** attempt * 3)
                continue
            break
        if r.status_code != 200:
            raise DataError(f"alpaca bars {r.status_code}: {r.text[:200]}")
        body = r.json()
        for sym, bars in (body.get("bars") or {}).items():
            for b in bars:
                rows.append((sym, b["t"], b["o"], b["h"], b["l"], b["c"], b["v"]))
        token = body.get("next_page_token")
        if not token:
            break
        params["page_token"] = token
        time.sleep(0.35)
    if not rows:
        raise DataError("alpaca returned no bars")
    return pd.DataFrame(rows, columns=["symbol", "t", *FIELDS])


def _to_market_data(long: pd.DataFrame, timeframe: str, source: str) -> MarketData:
    t = pd.to_datetime(long["t"], utc=True).dt.tz_convert("America/New_York")
    long = long.assign(t=t.dt.normalize().dt.tz_localize(None) if timeframe == "1Day" else t)
    if timeframe != "1Day":  # regular session only; Alpaca intraday bars include extended hours
        tod = long["t"].dt.strftime("%H:%M")
        long = long[(tod >= "09:30") & (tod < "16:00")]
    frames = {f: long.pivot_table(index="t", columns="symbol", values=f, aggfunc="last").sort_index() for f in FIELDS}
    return MarketData(**frames, timeframe=timeframe, source=source)


def load_alpaca(symbols, start, end, timeframe="1Day", feed="sip", fallback_feed="iex",
                adjustment="all", use_cache=True) -> MarketData:
    """Fetch bars from Alpaca (with a disk cache). `end` of "latest" means 20 minutes ago."""
    if end == "latest":
        end_ts = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=20)
        end = end_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        cache_end = end_ts.strftime("%Y-%m-%d")
    else:
        cache_end = end
    key = hashlib.sha256(json.dumps([sorted(symbols), start, cache_end, timeframe, feed, adjustment]).encode()).hexdigest()[:20]
    path = CACHE_DIR / f"bars_{timeframe}_{key}.csv.gz"
    long = None
    if use_cache and path.exists():
        cached = pd.read_csv(path)
        if "feed" in cached.columns and cached["feed"].nunique() == 1:   # entries without provenance are refetched
            long, used = cached.drop(columns="feed"), str(cached["feed"].iloc[0])
    if long is None:
        try:
            long, used = _fetch_alpaca(symbols, start, end, timeframe, feed, adjustment), feed
        except DataError as e:
            if fallback_feed and fallback_feed != feed and ("403" in str(e) or "subscription" in str(e).lower()):
                long, used = _fetch_alpaca(symbols, start, end, timeframe, fallback_feed, adjustment), fallback_feed
            else:
                raise
        if use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            long.assign(feed=used).to_csv(path, index=False)
    return _to_market_data(long, timeframe, source=f"alpaca:{used}")


# ---------------------------------------------------------------- synthetic

def synthetic(symbols, start="2016-01-01", end="2026-06-30", timeframe="1Day", seed=7) -> MarketData:
    """Deterministic fake prices for tests and offline smoke runs. Never promotable."""
    rng = np.random.default_rng(seed)
    if timeframe == "1Day":
        idx = pd.bdate_range(start, end)
    else:
        minutes = int(timeframe.replace("Min", ""))
        days = pd.bdate_range(start, end)
        per_day = pd.timedelta_range("09:30:00", "15:59:00", freq=f"{minutes}min")
        idx = pd.DatetimeIndex([d + o for d in days for o in per_day]).tz_localize("America/New_York")
    n, k = len(idx), len(symbols)
    scale = 1.0 if timeframe == "1Day" else np.sqrt(int(timeframe.replace("Min", "")) / 390)
    market = rng.normal(0.0003 * scale**2, 0.011 * scale, n)
    regime = np.sign(np.sin(np.arange(n) / (250 if timeframe == "1Day" else 2000))) * 0.0002 * scale
    beta = rng.uniform(0.7, 1.3, k)
    drift = rng.normal(0.0001, 0.0002, k) * scale**2
    idio = rng.normal(0, 0.012 * scale, (n, k))
    rets = (market + regime)[:, None] * beta + drift + idio
    close = 100 * rng.uniform(0.5, 3, k) * np.exp(np.cumsum(rets, axis=0))
    gap = rng.normal(0, 0.003 * scale, (n, k))
    open_ = np.vstack([close[:1], close[:-1]]) * np.exp(gap)
    hi = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, (n, k))))
    lo = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, (n, k))))
    vol = rng.uniform(5e6, 3e7, (n, k)) * (scale if timeframe != "1Day" else 1)
    mk = lambda a: pd.DataFrame(a, index=idx, columns=symbols)
    return MarketData(mk(open_), mk(hi), mk(lo), mk(close), mk(vol), timeframe=timeframe, source=f"synthetic:{seed}")
