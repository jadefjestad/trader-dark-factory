"""Hypothesis: short sellers are informed (Boehmer, Jones and Zhang 2008; Diether, Lee and Werner
2009): a rise in a stock's daily short-sale share of volume predicts lower returns over the following
weeks, and a fall predicts higher returns. Levels differ a lot across stocks for structural reasons
(market-maker hedging), so the signal is each stock's recent short-volume ratio relative to its own
norm. Buy the 8 large caps whose short-sale share has dropped the most.

Signal: mean FINRA short_volume_ratio over the last 21 bars minus its mean over the last 126 bars
(the panel is usable from the bar after each trade date; data starts 2019). Monthly rebalance,
equal weight, 10% vol target. Row t uses data public by bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowAbnormalShortVolume(Strategy):
    name = "low_abnormal_short_volume"
    lookback = 200
    extra_data = ("short_volume_ratio",)
    params = {"short_window": 21, "long_window": 126, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        svr = md.extra["short_volume_ratio"].reindex(columns=c.columns)
        S, L = int(p["short_window"]), int(p["long_window"])
        score = svr.rolling(S, min_periods=S * 2 // 3).mean() - svr.rolling(L, min_periods=L * 2 // 3).mean()
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
