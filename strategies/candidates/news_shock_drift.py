"""Hypothesis (issue #48): prices keep drifting for days after a burst of news, in the direction of its
tone (Chan 2003; Tetlock, Saar-Tsechansky & Macskassy 2008). Buying a stock the bar a news-count spike
arrives with positive headline tone, and holding it for 10 bars, earns a multi-day drift that is
unrelated to momentum, giving validation Sharpe above 0.3 with low correlation to the champion.

A new base signal (not a filter on the champion). Each event takes one of `slots` equal sleeves; the rest
stays in cash. News counts and tone come from Alpaca news; an article counts for bar t only if published
by 16:00 New York time on t, and the backtest fills at t+1's open.
"""
from strategies.base import Strategy


class NewsShockDrift(Strategy):
    name = "news_shock_drift"
    lookback = 90
    extra_data = ("news_count", "news_sentiment")
    params = {"base_window": 60, "spike": 3.0, "min_articles": 3, "hold": 10, "slots": 8}

    def target_weights(self, md):
        p = self.params
        cols = md.close.columns
        count = md.extra["news_count"].reindex(columns=cols).fillna(0.0)
        tone = md.extra["news_sentiment"].reindex(columns=cols).fillna(0.0)
        bw = int(p["base_window"])
        base = count.shift(1).rolling(bw, min_periods=bw).mean()
        event = (count >= p["min_articles"]) & (count > p["spike"] * base) & (tone > 0)
        hold = max(1, int(round(p["hold"])))
        active = event.astype(float).rolling(hold, min_periods=1).max() > 0
        active &= md.close.notna()
        slots = int(p["slots"])
        w = active.astype(float) / slots
        n = active.sum(axis=1)
        over = n > slots                        # more live events than sleeves: share the book equally
        w[over] = active[over].astype(float).div(n[over], axis=0)
        return w
