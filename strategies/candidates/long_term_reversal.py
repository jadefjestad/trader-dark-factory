"""Hypothesis: long-term reversal (De Bondt and Thaler 1985): stocks with the worst returns over the
previous three to five years outperform as investors' overreaction to persistent bad news fades.
Skipping the most recent year avoids the opposite (momentum) effect. None of the factory's candidates
look this far back. Buy the 8 large caps with the lowest return from 36 months ago to 12 months ago.

Monthly rebalance, equal weight, 10% vol target. Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LongTermReversal(Strategy):
    name = "long_term_reversal"
    lookback = 800
    params = {"formation": 756, "skip": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        F, S = int(p["formation"]), int(p["skip"])
        score = c.shift(S) / c.shift(F) - 1.0
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
