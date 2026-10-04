"""Earnings-announcement reactions from EDGAR 8-K Item 2.02 filings (issue #66).

Analyst estimates are paid data, so the surprise is proxied by the market's own reaction: the
abnormal return (stock minus the equal-weight universe) from the close before the announcement bar
to the close after it. Before-open releases (accepted before 16:00 New York time on day d) have
announcement bar d; after-close releases have announcement bar d+1 (factory.edgar.available_bar).
The window [b-1 close, b+1 close] therefore covers the reaction day and the day after either way,
and the value is stamped on bar b+1, the first close at which it is fully known.

Panels (one column per symbol):
- `earnings_reaction`: abnormal return of the latest announcement, carried forward until the next.
- `earnings_age`: bars since that reaction was stamped (0 on the stamping bar).
Both are NaN before a symbol's first announcement in the data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factory import edgar

PANEL_NAMES = ("earnings_reaction", "earnings_age")
MIN_GAP_DAYS = 20     # a second 2.02 filing within this many days (a correction) is not a new announcement


def announcements(filings: pd.DataFrame) -> pd.DataFrame:
    """One row per earnings release: symbol, accessionNumber, filingDate, acceptanceDateTime."""
    f = filings[(filings["form"] == "8-K") & filings["items"].fillna("").astype(str).str.contains("2.02", regex=False)]
    f = f.sort_values(["symbol", "filingDate"])
    keep = []
    for _, g in f.groupby("symbol"):
        last = None
        for i, d in zip(g.index, pd.to_datetime(g["filingDate"])):
            if last is None or (d - last).days > MIN_GAP_DAYS:
                keep.append(i)
                last = d
    return f.loc[keep, ["symbol", "accessionNumber", "filingDate", "acceptanceDateTime"]].reset_index(drop=True)


def panels(events: pd.DataFrame, close: pd.DataFrame) -> dict:
    idx = pd.DatetimeIndex(close.index)
    symbols = list(close.columns)
    reaction = pd.DataFrame(np.nan, index=close.index, columns=symbols)
    stamped = pd.DataFrame(np.nan, index=close.index, columns=symbols)
    ev = events[events["symbol"].isin(symbols)]
    bars = edgar.available_bar(edgar.acceptance_times(ev["acceptanceDateTime"]), ev["filingDate"], idx)
    px = close.to_numpy(dtype=float)
    pos_all = np.arange(len(idx))
    for s, b in zip(ev["symbol"], bars):
        if pd.isna(b):
            continue
        p = idx.get_loc(pd.Timestamp(b))
        if p < 1 or p + 1 >= len(idx):
            continue
        r = px[p + 1] / px[p - 1] - 1.0
        c = symbols.index(s)
        if not np.isfinite(r[c]):
            continue
        reaction.iat[p + 1, c] = r[c] - np.nanmean(r)
        stamped.iat[p + 1, c] = p + 1
    age = pd.DataFrame(pos_all[:, None] - stamped.ffill().to_numpy(), index=close.index, columns=symbols)
    return {"earnings_reaction": reaction.ffill(), "earnings_age": age}


def synthetic_filings(symbols: list[str], start="2014-01-01", end="2026-06-30") -> pd.DataFrame:
    """Quarterly 8-K 2.02 releases (alternating before the open and after the close) plus a correction."""
    rows = []
    for i, s in enumerate(symbols):
        for k, d in enumerate(pd.date_range(start, end, freq="QS") + pd.Timedelta(days=25 + i % 7)):
            while d.weekday() >= 5:
                d += pd.Timedelta(days=1)
            hhmm = "07:05:00" if k % 2 else "16:31:00"
            rows.append({"symbol": s, "accessionNumber": f"E{i:03d}-{k:04d}", "form": "8-K", "items": "2.02,9.01",
                         "filingDate": f"{d:%Y-%m-%d}", "acceptanceDateTime": f"{d:%Y-%m-%d}T{hhmm}.000Z"})
            if k == 3:   # same-quarter correction, not a new announcement
                c = d + pd.Timedelta(days=3)
                rows.append({**rows[-1], "accessionNumber": f"E{i:03d}-{k:04d}c", "filingDate": f"{c:%Y-%m-%d}",
                             "acceptanceDateTime": f"{c:%Y-%m-%d}T10:00:00.000Z"})
    return pd.DataFrame(rows)
