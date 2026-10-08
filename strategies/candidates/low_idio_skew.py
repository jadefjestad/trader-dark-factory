"""Hypothesis: investors overpay for lottery-like stocks with positively skewed returns, so stocks with
low idiosyncratic skewness earn more (Boyer, Mitton and Vorkink 2010; Bali, Cakici and Whitelaw
2011). Skewness is a different trait from volatility (low_idio_vol, PR #128, failed) and from the
single worst-day measure (low_max_return, PR #121). Rank stocks on the 252-day skewness of their
beta-adjusted residual returns, hold the 8 lowest at a 10% vol target, rebalanced monthly.

Beta is estimated over the same 252 days against the equal-weight universe.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowIdioSkew(Strategy):
    name = "low_idio_skew"
    lookback = 520
    params = {"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def vol_scaled(self, picks, rets):
        p = self.params
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, int(p["rebalance_every"]))):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"])).ffill().fillna(0.0)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        L, n = int(p["window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.shift(L).mul(mkt, axis=0)
        score = resid.rolling(L, min_periods=L).skew()
        rank = score.rank(axis=1, ascending=True, method="first")
        w = self.vol_scaled((rank <= n) & score.notna(), rets)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
