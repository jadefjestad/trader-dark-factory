"""Performance metrics computed from a BacktestResult (net of costs)."""
from __future__ import annotations

import math
from statistics import NormalDist

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


def deflated_sharpe(returns: pd.Series, trials: int) -> dict:
    """Probability that the true Sharpe is above zero after picking the best of `trials` experiments.

    Bailey & Lopez de Prado (2014): the benchmark Sharpe is the expected maximum of `trials` Sharpe
    estimates that are pure noise (their variance taken as the per-period sampling variance 1/T), and the
    test corrects for skew and fat tails. Values near 1 mean the result is unlikely to be luck."""
    r = pd.Series(returns).dropna()
    t = len(r)
    sd = float(r.std(ddof=1)) if t > 2 else 0.0
    if t < 30 or sd <= 0:
        return {"trials": int(trials), "probability": None}
    sr = float(r.mean()) / sd                      # per-period Sharpe
    z = (r - r.mean()) / sd
    skew, kurt = float((z ** 3).mean()), float((z ** 4).mean())
    n = max(int(trials), 1)
    nd, gamma = NormalDist(), 0.5772156649
    sr0 = 0.0 if n == 1 else math.sqrt(1.0 / t) * ((1 - gamma) * nd.inv_cdf(1 - 1.0 / n)
                                                   + gamma * nd.inv_cdf(1 - 1.0 / (n * math.e)))
    denom = 1 - skew * sr + (kurt - 1) / 4 * sr ** 2
    if denom <= 0:
        return {"trials": n, "probability": None}
    prob = nd.cdf((sr - sr0) * math.sqrt(t - 1) / math.sqrt(denom))
    return {"trials": n, "probability": round(prob, 4), "benchmark_annual_sharpe": round(sr0 * math.sqrt(252), 3)}
