"""Seconds-level history for the streaming tiers (issue #75): Alpaca historical trades and quotes,
cached per completed day, and fixed-boundary seconds bars built from them.

A bar is labelled by its END time and holds only prints stamped strictly before that end, the same
availability rule as the live BarBuilder (factory/stream/bars.py) and the #68 intraday pipeline: a
strategy may act on bar E from time E, and factory/stream/fills.py fills it at the first quote at or
after E plus latency. Any failed download raises DataError (fail closed).

    from factory.stream import history
    q = history.load_day("quotes", ["AAPL"], dt.date(2026, 10, 2))
    bars = history.seconds_bars(history.load_day("trades", ["AAPL"], day), q, seconds=5)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import time

import pandas as pd

from factory.data import CACHE_DIR, DataError, _alpaca_headers
from factory.stream.fills import QUOTE_COLUMNS

URLS = {"quotes": "https://data.alpaca.markets/v2/stocks/quotes",
        "trades": "https://data.alpaca.markets/v2/stocks/trades"}
TRADE_COLUMNS = ["time", "symbol", "price", "size"]
NY = "America/New_York"


def _get(url, **kw):
    import requests
    return requests.get(url, timeout=60, **kw)


def parse(kind: str, body: dict) -> pd.DataFrame:
    """One API page ({kind: {symbol: [records]}}) -> tidy rows. Pure; unit-tested offline."""
    rows = []
    for sym, recs in (body.get(kind) or {}).items():
        for r in recs:
            if kind == "quotes":
                rows.append((r["t"], sym, r.get("bp"), r.get("ap"), r.get("bs"), r.get("as")))
            else:
                rows.append((r["t"], sym, r.get("p"), r.get("s")))
    cols = QUOTE_COLUMNS if kind == "quotes" else TRADE_COLUMNS
    df = pd.DataFrame(rows, columns=cols)
    df["time"] = pd.to_datetime(df["time"], utc=True, format="ISO8601")
    for c in cols[2:]:
        df[c] = df[c].astype(float)
    return df


def fetch(kind: str, symbols: list[str], start: pd.Timestamp, end: pd.Timestamp, feed: str = "sip",
          pause: float = 0.3) -> pd.DataFrame:
    """Every record in [start, end) for `symbols`, following next_page_token."""
    params = {"symbols": ",".join(symbols), "feed": feed, "limit": 10000,
              "start": start.tz_convert("UTC").isoformat().replace("+00:00", "Z"),
              "end": end.tz_convert("UTC").isoformat().replace("+00:00", "Z")}
    frames = []
    while True:
        r = None
        for attempt in range(4):
            try:
                r = _get(URLS[kind], params=params, headers=_alpaca_headers())
            except Exception:
                r = None
            if r is not None and r.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(2 ** attempt)
        if r is None or r.status_code != 200:
            raise DataError(f"Alpaca historical {kind}: {getattr(r, 'status_code', 'no response')}")
        body = r.json()
        frames.append(parse(kind, body))
        if not body.get("next_page_token"):
            break
        params["page_token"] = body["next_page_token"]
        time.sleep(pause)
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(["time", "symbol"], kind="stable").reset_index(drop=True)


def load_day(kind: str, symbols: list[str], day: dt.date, feed: str = "sip", use_cache: bool = True) -> pd.DataFrame:
    """Regular-session records for one day. Only completed days are cached (today's may still grow)."""
    open_, close = (pd.Timestamp(f"{day} {t}", tz=NY) for t in ("09:30", "16:00"))
    key = hashlib.sha256(",".join(sorted(symbols)).encode()).hexdigest()[:10]
    path = CACHE_DIR / f"{kind}_{feed}_{day:%Y-%m-%d}_{key}.csv.gz"
    if use_cache and path.exists():
        df = pd.read_csv(path)
        df["time"] = pd.to_datetime(df["time"], utc=True, format="ISO8601")
        return df
    df = fetch(kind, symbols, open_, close, feed)
    if use_cache and day < pd.Timestamp.now(tz=NY).date():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    return df


def seconds_bars(trades: pd.DataFrame, quotes: pd.DataFrame | None, seconds: int) -> dict[str, pd.DataFrame]:
    """Wide OHLCV panels (plus bid and ask) indexed by bar END. A bar holds prints with start <= t < end;
    an interval with no trade repeats the previous close with volume 0, and bid/ask are the last quote
    before the end."""
    if seconds <= 0 or 86400 % seconds:
        raise ValueError("bar length must divide a day evenly")
    rule = f"{seconds}s"
    t = trades.set_index("time")
    end_of = lambda s: s.index.floor(rule) + pd.Timedelta(seconds=seconds)
    g = t.groupby([end_of(t), t["symbol"]])
    out = {"open": g["price"].first(), "high": g["price"].max(), "low": g["price"].min(),
           "close": g["price"].last(), "volume": g["size"].sum()}
    out = {k: v.unstack("symbol") for k, v in out.items()}
    idx = pd.date_range(out["close"].index.min(), out["close"].index.max(), freq=rule)
    out = {k: v.reindex(idx) for k, v in out.items()}
    out["close"] = out["close"].ffill()
    for k in ("open", "high", "low"):
        out[k] = out[k].fillna(out["close"])
    out["volume"] = out["volume"].fillna(0.0)
    if quotes is not None and len(quotes):
        q = quotes.set_index("time")
        for side in ("bid", "ask"):
            last = q.groupby([end_of(q), q["symbol"]])[side].last().unstack("symbol")
            out[side] = last.reindex(idx.union(last.index)).ffill().reindex(idx).reindex(columns=out["close"].columns)
    return out
