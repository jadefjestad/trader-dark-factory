"""Strategy interface. PROTECTED.

A strategy turns market data into target portfolio weights. A row that is entirely NaN means "no
decision: keep the drifted holdings" (no trades); any other NaN is treated as zero in backtests and
rejected by the live executor. Row t may only use data up to and
including bar t (the evaluator re-runs on truncated data to prove this). Weights are fractions of
equity per symbol; negative weights are shorts and are rejected while risk limits forbid shorting.
Strategies never place orders, read files, or touch the network.

Extra data: list panel names in `extra_data` (e.g. ("news_count",)) and read them from md.extra[name],
a DataFrame aligned to md.close. Row t of every panel only reflects information available by bar t's
close. If a panel cannot be loaded, the executor places no orders.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factory.data import MarketData


class Strategy:
    name: str = "unnamed"
    timeframe: str = "1Day"      # "1Day", "15Min" or "5Min"
    lookback: int = 300          # bars of history needed before signals are meaningful
    extra_data: tuple = ()       # extra panels needed, from factory.extras.PANELS
    params: dict = {}

    def __init__(self, **overrides):
        self.params = {**type(self).params, **overrides}

    def target_weights(self, md: MarketData) -> pd.DataFrame:
        raise NotImplementedError


def equal_weight(mask: pd.DataFrame, slots: int | None = None) -> pd.DataFrame:
    """Weight True cells per row at 1/slots (or 1/count when slots is None), zero elsewhere."""
    m = mask.fillna(False).astype(float)
    if slots:
        return m / float(slots)
    n = m.sum(axis=1).replace(0, float("nan"))
    return m.div(n, axis=0).fillna(0.0)


REBALANCE_EPOCH = np.datetime64("2000-01-03")


def rebalance_mask(index: pd.Index, every: int) -> np.ndarray:
    """True on the first bar of each `every`-business-day bucket counted from a fixed epoch.

    Anchoring to the calendar (not to the first row) gives the same rebalance dates whether a strategy
    sees ten years of history in a backtest or only its lookback window in live execution."""
    days = pd.DatetimeIndex(index)
    days = (days.tz_localize(None) if days.tz is not None else days).normalize().values.astype("datetime64[D]")
    bucket = np.busday_count(REBALANCE_EPOCH, days) // every
    return np.r_[True, bucket[1:] != bucket[:-1]]


def hold_between_rebalances(w: pd.DataFrame, every: int) -> pd.DataFrame:
    """Trade only on calendar-anchored rebalance bars; rows in between are all-NaN ("hold")."""
    keep = rebalance_mask(w.index, every)
    return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
