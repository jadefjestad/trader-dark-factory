"""Strategy interface. PROTECTED.

A strategy turns market data into target portfolio weights. Row t may only use data up to and
including bar t (the evaluator re-runs on truncated data to prove this). Weights are fractions of
equity per symbol; negative weights are shorts and are rejected while risk limits forbid shorting.
Strategies never place orders, read files, or touch the network.
"""
from __future__ import annotations

import pandas as pd

from factory.data import MarketData


class Strategy:
    name: str = "unnamed"
    timeframe: str = "1Day"      # "1Day", "15Min" or "5Min"
    lookback: int = 300          # bars of history needed before signals are meaningful
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


def hold_between_rebalances(w: pd.DataFrame, every: int) -> pd.DataFrame:
    """Keep weights fixed except on every `every`-th bar (causal: uses only past rows)."""
    keep = pd.Series(range(len(w)), index=w.index) % every == 0
    return w.where(keep, other=float("nan")).ffill().fillna(0.0)
