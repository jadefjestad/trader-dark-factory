"""Extra data panels a strategy can request through `Strategy.extra_data`.

Each builder returns a DataFrame aligned to md.index whose row t only reflects information available
by bar t's close. Loading failures raise DataError, so a strategy that needs a panel never trades
without it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factory.data import DataError, MarketData


def _news_count(md: MarketData, source: str) -> pd.DataFrame:
    if source == "synthetic":   # deterministic fake counts for tests and offline smoke runs
        rng = np.random.default_rng(11)
        lam = rng.uniform(0.5, 6.0, len(md.symbols))
        return pd.DataFrame(rng.poisson(lam, (len(md.index), len(md.symbols))).astype(float),
                            index=md.index, columns=md.symbols)
    from factory import news
    start = (pd.Timestamp(md.index[0]) - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    arts = news.load(md.symbols, start, "latest")
    if arts.empty:
        raise DataError("no news articles loaded")
    return news.count_panel(arts, pd.DatetimeIndex(md.index), md.symbols)


def _macro(md: MarketData, source: str) -> pd.DataFrame:
    from factory import macro
    if source == "synthetic":   # smooth deterministic fake series for tests and offline smoke runs
        rng = np.random.default_rng(13)
        days = pd.bdate_range(pd.Timestamp(md.index[0]) - pd.Timedelta(days=10), md.index[-1])
        raw = pd.DataFrame(np.cumsum(rng.normal(0, 0.05, (len(days), len(macro.SERIES))), axis=0) + 3.0,
                           index=days, columns=list(macro.SERIES))
    else:
        raw = macro.load()
    out = macro.panel(raw, pd.DatetimeIndex(md.index))
    if out.iloc[-1].isna().any():
        raise DataError(f"macro series missing on the latest bar: {out.columns[out.iloc[-1].isna()].tolist()}")
    return out


PANELS = {"news_count": _news_count, "macro": _macro}


def attach(md: MarketData, names, source: str) -> MarketData:
    """Return md with the requested panels in md.extra. Unknown names are an error."""
    names = list(names or ())
    unknown = [n for n in names if n not in PANELS]
    if unknown:
        raise DataError(f"unknown extra data {unknown}; available: {sorted(PANELS)}")
    if md.timeframe != "1Day" and names:
        raise DataError("extra data panels are daily only")
    extra = dict(md.extra)
    for n in names:
        extra[n] = PANELS[n](md, source)
    return MarketData(md.open, md.high, md.low, md.close, md.volume, timeframe=md.timeframe, source=md.source,
                      extra=extra)
