"""Hypothesis: residual_reversal (PR #136: validation 0.71, holdout about 1.9) buys the 8 stocks with
the worst 21-day residual returns. Losses on unusually heavy volume often reflect news that keeps
moving the price, while losses on light volume are more often liquidity-driven and revert (Lee and
Swaminathan 2000; Llorente et al. 2002). Taking the 16 worst residual losers and keeping the 8 with
the lowest relative volume (21-day average over 252-day average) should raise the reversal edge.

One change versus residual_reversal: a light-volume screen on twice the candidate list.
Row t uses closes and volumes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class QuietResidualReversal(Strategy):
    name = "quiet_residual_reversal"
    lookback = 340
    params = {"beta_window": 252, "window": 21, "top_n": 8, "screen_n": 16, "volume_window": 21, "rebalance_every": 5,
              "vol_target": 0.10, "vol_window": 60}

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
        B, W, n = int(p["beta_window"]), int(p["window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(B, min_periods=B).cov(mkt).div(mkt.rolling(B, min_periods=B).var(), axis=0)
        resid = rets - beta.shift(W).mul(mkt, axis=0)
        win = resid.rolling(W, min_periods=W)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=True, method="first")
        vol = md.volume.reindex(columns=rets.columns).astype(float)
        V = int(p["volume_window"])
        rel = vol.rolling(V, min_periods=V).mean() / vol.rolling(B, min_periods=B).mean()
        cand = (rank <= int(p["screen_n"])) & score.notna() & rel.notna()
        vrank = rel.where(cand).rank(axis=1, ascending=True, method="first")
        w = self.vol_scaled(vrank <= n, rets)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
