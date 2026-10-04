"""Performance metrics computed from a BacktestResult (net of costs)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from factory.backtest import BacktestResult


def periods_per_year(index: pd.Index, timeframe: str) -> float:
    if timeframe == "1Day":
        return 252.0
    days = max(len(set(pd.DatetimeIndex(index).date)), 1)
    return 252.0 * len(index) / days


def summarize(res: BacktestResult, start=None, end=None) -> dict:
    r = res.returns.loc[start:end]
    eq = res.equity.loc[start:end]
    if len(r) < 2:
        return {"bars": len(r)}
    ppy = periods_per_year(r.index, res.meta.get("timeframe", "1Day"))
    years = len(r) / ppy
    total = float(eq.iloc[-1] / eq.iloc[0] - 1.0) if eq.iloc[0] > 0 else -1.0
    vol = float(r.std(ddof=0) * np.sqrt(ppy))
    mean = float(r.mean() * ppy)
    downside = float(r[r < 0].std(ddof=0) * np.sqrt(ppy)) if (r < 0).any() else 0.0
    dd = float((eq / eq.cummax() - 1.0).min())
    w = res.holdings.loc[start:end]
    trades = int(res.fills.loc[start:end].sum())   # actual fills, including drift rebalancing
    return {
        "bars": int(len(r)),
        "total_return": round(total, 6),
        "cagr": round(float((1 + total) ** (1 / years) - 1) if years > 0 and total > -1 else -1.0, 6),
        "annual_vol": round(vol, 6),
        "sharpe": round(mean / vol, 4) if vol > 0 else 0.0,
        "sortino": round(mean / downside, 4) if downside > 0 else 0.0,
        "max_drawdown": round(-dd, 6),
        "annual_turnover": round(float(res.turnover.loc[start:end].sum() / years), 4) if years > 0 else 0.0,
        "cost_drag": round(float(res.costs.loc[start:end].sum() / years), 6) if years > 0 else 0.0,
        "avg_exposure": round(float(w.abs().sum(axis=1).mean()), 4),
        "trades": trades,
    }
