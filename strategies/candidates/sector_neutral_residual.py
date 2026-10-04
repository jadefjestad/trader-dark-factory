"""Hypothesis: the residual-momentum champion often loads on one sector (e.g. five tech names at once), so
its drawdowns come from sector rotations rather than stock-specific drift. Ranking on the residual score
minus its sector's average keeps the stock-level signal while spreading picks across sectors, lowering
drawdown and raising validation Sharpe.

One change versus residual_vol_momentum: scores are demeaned within GICS-style sectors before ranking.
Sector labels are fixed (no look-ahead: they do not depend on prices); unknown symbols form their own group.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask

SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "NVDA": "tech", "AVGO": "tech", "ADBE": "tech", "CSCO": "tech",
    "GOOGL": "comm", "META": "comm", "AMZN": "discretionary", "HD": "discretionary",
    "JPM": "financials", "BAC": "financials", "V": "financials", "MA": "financials",
    "UNH": "health", "LLY": "health", "JNJ": "health", "MRK": "health",
    "XOM": "energy", "CVX": "energy",
    "PG": "staples", "KO": "staples", "PEP": "staples", "COST": "staples", "WMT": "staples",
}


class SectorNeutralResidualMomentum(Strategy):
    name = "sector_neutral_residual"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        L, S = int(p["lookback"]), int(p["skip"])
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        score = win.sum() / win.std()
        groups = [SECTORS.get(s, s) for s in score.columns]
        score = score - score.T.groupby(groups).transform("mean").T
        rank = score.rank(axis=1, ascending=False)
        w = equal_weight((rank <= int(p["top_n"])) & score.notna(), slots=int(p["top_n"]))
        vw = int(p["vol_window"])
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
