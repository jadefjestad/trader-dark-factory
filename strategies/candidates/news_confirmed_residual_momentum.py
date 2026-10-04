"""Hypothesis (issue #29): price moves that come with news keep drifting, while moves without news tend to
reverse (Chan 2003, "Stock price reaction to news and no-news"). Restricting the residual-momentum
champion to stocks whose news attention over the last quarter is at or above their own one-year norm
should keep the winners whose rise is news-driven and drop the ones drifting on noise.

One change versus residual_vol_momentum: stocks with below-normal recent news coverage are not eligible.
News counts come from Alpaca (Benzinga); an article counts for bar t only if published by t's close.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class NewsConfirmedResidualMomentum(Strategy):
    name = "news_confirmed_residual_momentum"
    lookback = 520
    extra_data = ("news_count",)
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60,
              "news_window": 63, "min_attention": 1.0}

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

        news = md.extra["news_count"].reindex(columns=c.columns).fillna(0.0)
        nw = int(p["news_window"])
        recent = news.rolling(nw, min_periods=nw).mean()
        normal = news.rolling(252, min_periods=252).mean()
        attention = recent / normal.where(normal > 0)
        eligible = attention >= p["min_attention"]

        score = score.where(eligible)
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
