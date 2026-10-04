"""Hypothesis (issue #64): open-market purchases by insiders, especially by several insiders at once,
predict positive abnormal returns over the next one to six months (Lakonishok and Lee 2001; Cohen,
Malloy and Pomorski 2012). Holding each large cap for the 90 days after any insider buys it on the
open market, ranked by the number of distinct buyers and then the dollar value, should earn a
positive validation Sharpe as a sleeve the champion could later blend with.

Coverage caveat measured before this test: only 522 purchases across the 25 names since 2014 (151 of
them in 2020), so the sleeve is often in cash and may fail the minimum-trade gate; that is a result.

Purchases count from the bar their Form 4 was accepted by EDGAR, never from the trade date.

One change versus the factory's other candidates: the signal is insider buying.
"""
from strategies.base import Strategy, hold_between_rebalances


class InsiderClusterBuying(Strategy):
    name = "insider_cluster_buying"
    lookback = 30
    extra_data = ("insider_buyers", "insider_buy_value")
    params = {"min_buyers": 1, "slots": 8, "rebalance_every": 5}

    def target_weights(self, md):
        p = self.params
        c = md.close
        buyers = md.extra["insider_buyers"].reindex(columns=c.columns).fillna(0.0)
        value = md.extra["insider_buy_value"].reindex(columns=c.columns).fillna(0.0)
        live = buyers >= p["min_buyers"]
        score = (buyers + value.rank(axis=1, pct=True) * 0.5).where(live)
        rank = score.rank(axis=1, ascending=False, method="first")
        n = int(p["slots"])
        w = ((rank <= n) & score.notna()).astype(float) / n
        return hold_between_rebalances(w, int(p["rebalance_every"]))
