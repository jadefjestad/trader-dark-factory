"""Hypothesis: momentum profits come mostly from returns 12 to 7 months ago, not from the most recent
six months (Novy-Marx 2012, "Is momentum really momentum?"). Among large caps, holding the eight stocks
with the highest log return from bar t-252 to bar t-126, sized to a 10% volatility target and
rebalanced monthly, should earn a positive validation Sharpe and differ from the 12-1 momentum the
champion family uses because the recent half-year is excluded.

One change versus the factory's other candidates: the ranking signal is the 12-to-7 month return.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class IntermediateMomentum(Strategy):
    name = "intermediate_momentum"
    lookback = 300
    params = {"far": 252, "near": 126, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        score = np.log(c.shift(int(p["near"])) / c.shift(int(p["far"])))
        rank = score.rank(axis=1, ascending=False, method="first")
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
