"""Hypothesis (issue #66): post-earnings-announcement drift. The market's own two-day reaction to an
earnings release (stock minus the equal-weight universe, from the close before the announcement bar
to the close after it) predicts returns in the same direction over the next few months (Brandt,
Kishore, Santa-Clara and Venkatachalam 2008), and works without paid analyst estimates. Holding the
large caps with the strongest positive reactions for about 60 bars after each release should earn
a positive validation Sharpe with turnover well under the 25x gate, because each name is held for a
quarter at most and new names only enter at weekly rebalances.

Announcement times come from EDGAR 8-K Item 2.02 acceptance timestamps, so before-open and
after-close releases are each measured from the right bar and nothing is known before it happens.

One change versus the factory's other candidates: the signal is the earnings reaction.
"""
from strategies.base import Strategy, hold_between_rebalances


class EarningsReactionDrift(Strategy):
    name = "earnings_reaction_drift"
    lookback = 100   # live data window must still contain the bar before a 60-bar-old release
    extra_data = ("earnings_reaction", "earnings_age")
    params = {"hold_bars": 60, "min_reaction": 0.02, "slots": 8, "rebalance_every": 5}

    def target_weights(self, md):
        p = self.params
        c = md.close
        reaction = md.extra["earnings_reaction"].reindex(columns=c.columns)
        age = md.extra["earnings_age"].reindex(columns=c.columns)
        live = (age <= int(p["hold_bars"])) & (reaction >= p["min_reaction"])
        score = reaction.where(live)
        rank = score.rank(axis=1, ascending=False, method="first")
        n = int(p["slots"])
        w = ((rank <= n) & score.notna()).astype(float) / n
        return hold_between_rebalances(w, int(p["rebalance_every"]))
