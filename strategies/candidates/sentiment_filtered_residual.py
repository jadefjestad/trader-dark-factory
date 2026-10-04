"""Hypothesis (issue #29): negative news language predicts weak returns over the following weeks (Tetlock
2007; Loughran & McDonald 2011). Dropping momentum winners whose headlines over the last month score net
negative avoids picks about to be hit by bad-news drift, raising the champion's validation Sharpe.

One change versus residual_vol_momentum: stocks with a negative 21-bar headline sentiment sum are not eligible.
Sentiment is the news_sentiment panel (fixed finance lexicon; an article counts for bar t only if
published by 16:00 New York time on t).
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class SentimentFilteredResidualMomentum(Strategy):
    name = "sentiment_filtered_residual"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    extra_data = ("news_sentiment",)
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60,
              "sentiment_window": 21}

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
        sw = int(p["sentiment_window"])
        mood = md.extra["news_sentiment"].reindex(columns=c.columns).fillna(0.0).rolling(sw, min_periods=sw).sum()
        score = score.where(mood >= 0)
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
