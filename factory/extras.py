"""Extra data panels a strategy can request through `Strategy.extra_data`.

Each builder returns a DataFrame aligned to md.index whose row t only reflects information available
by bar t's close. Loading failures raise DataError, so a strategy that needs a panel never trades
without it.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factory.data import DataError, MarketData


def _news_articles(md: MarketData) -> pd.DataFrame:
    from factory import news
    start = (pd.Timestamp(md.index[0]) - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    arts = news.load(md.symbols, start, "latest")
    if arts.empty:
        raise DataError("no news articles loaded")
    return arts


def _news_count(md: MarketData, source: str) -> pd.DataFrame:
    if source == "synthetic":   # deterministic fake counts for tests and offline smoke runs
        rng = np.random.default_rng(11)
        lam = rng.uniform(0.5, 6.0, len(md.symbols))
        return pd.DataFrame(rng.poisson(lam, (len(md.index), len(md.symbols))).astype(float),
                            index=md.index, columns=md.symbols)
    from factory import news
    return news.count_panel(_news_articles(md), pd.DatetimeIndex(md.index), md.symbols)


def _news_sentiment(md: MarketData, source: str) -> pd.DataFrame:
    if source == "synthetic":
        rng = np.random.default_rng(17)
        return pd.DataFrame(rng.integers(-2, 3, (len(md.index), len(md.symbols))).astype(float),
                            index=md.index, columns=md.symbols)
    from factory import news
    return news.sentiment_panel(_news_articles(md), pd.DatetimeIndex(md.index), md.symbols)


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


_SEC_MEMO: dict = {}


def _sec(md: MarketData, source: str, family: str) -> dict:
    """All panels of one SEC family (fundamentals, insiders, earnings), built once per dataset."""
    key = (family, source, tuple(md.symbols), md.index[0], md.index[-1], len(md.index))
    if key in _SEC_MEMO:
        return _SEC_MEMO[key]
    from factory import earnings, edgar, fundamentals, insiders
    syms, idx = md.symbols, pd.DatetimeIndex(md.index)
    if family == "fundamentals":
        if source == "synthetic":
            table = fundamentals.synthetic_table(syms)
            out = fundamentals.panels(table, fundamentals.synthetic_filings(table), idx, syms)
        else:
            out = fundamentals.panels(fundamentals.fetch(syms), edgar.filings(syms), idx, syms)
    elif family == "insiders":
        if source == "synthetic":
            out = insiders.panels(*insiders.synthetic_purchases(syms), idx, syms)
        else:
            fil = edgar.filings(syms)
            out = insiders.panels(insiders.fetch(syms, fil), fil, idx, syms)
    else:
        fil = earnings.synthetic_filings(syms) if source == "synthetic" else edgar.filings(syms)
        out = earnings.panels(earnings.announcements(fil), md.close)
    if len(_SEC_MEMO) > 8:
        _SEC_MEMO.clear()
    _SEC_MEMO[key] = out
    return out


def _sec_panel(family: str, name: str):
    return lambda md, source: _sec(md, source, family)[name].copy()


PANELS = {"news_count": _news_count, "news_sentiment": _news_sentiment, "macro": _macro,
          "gross_profitability": _sec_panel("fundamentals", "gross_profitability"),
          "eps_ttm": _sec_panel("fundamentals", "eps_ttm"),
          "eps_sue": _sec_panel("fundamentals", "eps_sue"),
          "insider_buyers": _sec_panel("insiders", "insider_buyers"),
          "insider_buy_value": _sec_panel("insiders", "insider_buy_value"),
          "earnings_reaction": _sec_panel("earnings", "earnings_reaction"),
          "earnings_age": _sec_panel("earnings", "earnings_age")}


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
