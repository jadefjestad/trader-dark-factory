"""Deterministic portfolio backtester.

Timing rule (no look-ahead): weights a strategy outputs on bar t may use data up to bar t's close.
They are filled at bar t+1's open, with slippage, half-spread and fees charged on the traded notional.
Returns are measured open-to-open, so a weight decided at t earns open[t+1] -> open[t+2].
An all-NaN weight row means "hold": no trades, positions drift with prices.
Intraday runs are forced flat by each session's final bar (no overnight holding).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from factory.data import MarketData


@dataclass
class BacktestResult:
    equity: pd.Series                 # equity at each fill time (bar opens)
    returns: pd.Series                # net period returns
    weights: pd.DataFrame             # target weights as decided (index = decision bar; NaN rows = hold)
    holdings: pd.DataFrame            # weights actually held after each fill
    turnover: pd.Series               # traded notional / equity at each fill
    costs: pd.Series                  # cost as a fraction of equity at each fill
    fills: pd.Series                  # executed (symbol) trades at each fill bar
    trades: int                       # total executed trades
    max_participation: float          # largest order / bar dollar volume
    meta: dict = field(default_factory=dict)


def _clean_weights(w: pd.DataFrame, md: MarketData) -> pd.DataFrame:
    w = w.reindex(index=md.index, columns=md.symbols).astype(float)
    w = w.replace([np.inf, -np.inf], 0.0)
    hold = w.isna().all(axis=1)
    w = w.fillna(0.0)
    w[hold] = np.nan
    return w


def _flatten_intraday(w: pd.DataFrame) -> pd.DataFrame:
    days = pd.Series(w.index.date, index=w.index)
    nxt = days.shift(-1)
    nxt2 = days.shift(-2)
    # zero the decision if the fill bar (t+1) is the session's last bar, or the session ends at t
    last_or_penultimate = (nxt != days) | (nxt2 != days)
    w = w.copy()
    w.loc[last_or_penultimate.values] = 0.0
    return w


def run(weights: pd.DataFrame, md: MarketData, costs: dict, initial_capital: float = 100_000.0) -> BacktestResult:
    w = _clean_weights(weights, md)
    if md.timeframe != "1Day":
        w = _flatten_intraday(w)

    op = md.open.reindex(columns=md.symbols).ffill()
    opv = op.values
    vol = md.volume.reindex(columns=md.symbols).fillna(0.0).values
    tradable = ~md.open.reindex(columns=md.symbols).isna().values
    wv = w.values
    hold_rows = np.isnan(wv).all(axis=1)
    n, k = wv.shape
    per_side = (costs.get("slippage_bps", 0) + costs.get("half_spread_bps", 0)) / 1e4
    sell_fee = costs.get("sell_fee_bps", 0) / 1e4

    equity = np.empty(n)
    rets = np.zeros(n)
    turn = np.zeros(n)
    cost = np.zeros(n)
    fills = np.zeros(n)
    equity[0] = initial_capital
    held = np.zeros(k)          # weights held after the most recent fill
    trades = 0
    max_part = 0.0
    applied = np.zeros((n, k))

    for t in range(1, n):
        # 1) mark held positions from open[t-1] to open[t]
        r = np.where(np.isfinite(opv[t]) & np.isfinite(opv[t - 1]) & (opv[t - 1] > 0), opv[t] / opv[t - 1] - 1.0, 0.0)
        gross = 1.0 + float(held @ r)
        drifted = held * (1.0 + r) / gross if gross > 0 else np.zeros(k)
        # 2) fill the target decided at bar t-1 at open[t]
        target = drifted.copy() if hold_rows[t - 1] else wv[t - 1].copy()
        target[~tradable[t]] = drifted[~tradable[t]]   # cannot trade a missing bar
        delta = target - drifted
        traded = np.abs(delta).sum()
        c = traded * per_side + np.clip(-delta, 0, None).sum() * sell_fee
        eq_before = equity[t - 1] * gross
        equity[t] = eq_before * (1.0 - c)
        rets[t] = equity[t] / equity[t - 1] - 1.0
        turn[t] = traded
        cost[t] = c
        changed = np.abs(delta) > 1e-6
        fills[t] = changed.sum()
        trades += int(changed.sum())
        if changed.any():
            dollar_vol = vol[t] * opv[t]
            with np.errstate(divide="ignore", invalid="ignore"):
                part = np.where(dollar_vol > 0, np.abs(delta) * eq_before / dollar_vol, np.where(changed, np.inf, 0))
            max_part = max(max_part, float(np.nanmax(part)))
        held = target
        applied[t] = held

    idx = md.index
    return BacktestResult(
        equity=pd.Series(equity, idx), returns=pd.Series(rets, idx), weights=w,
        holdings=pd.DataFrame(applied, idx, md.symbols), turnover=pd.Series(turn, idx), costs=pd.Series(cost, idx), fills=pd.Series(fills, idx), trades=trades,
        max_participation=max_part,
        meta={"timeframe": md.timeframe, "source": md.source},
    )
