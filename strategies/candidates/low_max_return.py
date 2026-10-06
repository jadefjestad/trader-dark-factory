"""Hypothesis: investors overpay for lottery-like stocks, so stocks with the largest single-day gain over
the past month earn lower future returns (Bali, Cakici and Whitelaw 2011, "Maxing out"). Among large
caps, holding the eight with the smallest maximum daily return over the last 21 trading days, sized to
a 10% volatility target and rebalanced monthly, should earn a positive validation Sharpe. The signal
uses the extreme of the return distribution, not its volatility, so it differs from low_vol_tilt.

One change versus the factory's other candidates: the ranking signal is the trailing 21-day maximum
daily return, lowest first.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowMaxReturn(Strategy):
    name = "low_max_return"
    lookback = 90
    params = {"window": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        win = int(p["window"])
        score = rets.rolling(win, min_periods=win).max()
        rank = score.rank(axis=1, ascending=True, method="first")
        n = int(p["top_n"])
        w = equal_weight((rank <= n) & score.notna(), slots=n)
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
