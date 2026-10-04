"""Hypothesis (issue #66 follow-up): the earnings-announcement premium sleeve (PR #87: validation Sharpe
0.97, in-sample 1.51) earns its return from the reporting calendar, not from past winners, so it should
be weakly correlated with the residual-momentum champion. Holding half the book in each, rebalanced
weekly, should beat the champion's validation Sharpe through diversification while staying under the
turnover and drawdown gates.

Sleeve 1 is residual_vol_momentum unchanged (monthly, 10% vol target); sleeve 2 is
earnings_announcement_premium unchanged. One change versus the champion: half the capital moves to
the announcement-premium sleeve.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualMomentumAnnouncementBlend(Strategy):
    name = "residual_momentum_announcement_blend"
    lookback = 520
    extra_data = ("earnings_age",)
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60,
              "window_start": 45, "window_end": 70, "min_slots": 8, "premium_share": 0.5, "blend_every": 5}

    def momentum_sleeve(self, c, rets):
        p = self.params
        L, S = int(p["lookback"]), int(p["skip"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        score = win.sum() / win.std()
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
        return hold_between_rebalances(w, int(p["rebalance_every"])).ffill().fillna(0.0)

    def premium_sleeve(self, md):
        p = self.params
        age = md.extra["earnings_age"].reindex(columns=md.close.columns)
        due = (age >= p["window_start"]) & (age <= p["window_end"])
        slots = due.sum(axis=1).clip(lower=p["min_slots"])
        return due.astype(float).div(slots, axis=0)

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        share = float(p["premium_share"])
        w = self.momentum_sleeve(c, rets) * (1 - share) + self.premium_sleeve(md) * share
        return hold_between_rebalances(w, int(p["blend_every"]))
