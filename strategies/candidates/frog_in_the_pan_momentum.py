"""Hypothesis: momentum built from many small daily gains persists longer than momentum built from a
few big jumps, because investors underreact to information that arrives gradually (Da, Gurun and
Warachka 2014, "Frog in the pan"). Information discreteness is ID = sign(PRET) * (%negative days -
%positive days) over the 12-1 month window; low ID means continuous momentum. Taking the sixteen
large caps with the highest 12-1 month return and keeping the eight with the lowest ID, sized to a 10%
volatility target and rebalanced monthly, should beat plain cross-sectional momentum (validation
Sharpe 0.91) on validation Sharpe.

One change versus 12-1 momentum: winners are filtered on information discreteness.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class FrogInThePanMomentum(Strategy):
    name = "frog_in_the_pan_momentum"
    lookback = 300
    params = {"lookback": 252, "skip": 21, "pool": 16, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        L, S = int(p["lookback"]), int(p["skip"])
        n_days = L - S
        pret = c.shift(S) / c.shift(L) - 1
        lagged = rets.shift(S)
        pos = (lagged > 0).astype(float).where(lagged.notna()).rolling(n_days, min_periods=n_days).mean()
        neg = (lagged < 0).astype(float).where(lagged.notna()).rolling(n_days, min_periods=n_days).mean()
        disc = np.sign(pret) * (neg - pos)
        mom_rank = pret.rank(axis=1, ascending=False, method="first")
        pool = (mom_rank <= int(p["pool"])) & disc.notna()
        id_rank = disc.where(pool).rank(axis=1, ascending=True, method="first")
        n = int(p["top_n"])
        w = equal_weight(id_rank <= n, slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, int(p["rebalance_every"]))):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
