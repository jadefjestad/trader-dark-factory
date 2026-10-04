"""Hypothesis (issue #66 follow-up): the earnings-announcement premium. Stocks earn higher returns in
the weeks around their scheduled earnings announcements, as risk and attention rise (Frazzini and
Lamont 2007; Barber, De George, Lehavy and Trueman 2013). Large caps report on a steady quarterly
cycle, so the bars since the last release predict when the next one is due without any look-ahead.
Holding the names whose last release was 45 to 70 bars ago (the run-up to and the days of the next
release) should beat holding them at random, with turnover far under the 25x gate.

The probe for PR #85 found this pattern in 2015 to 2023 (monthly rank correlation of bars-since-release
with next-month return 0.042, t 1.7); the holdout was never examined, and the literature predates it.

One change versus earnings_reaction_drift: the signal is the announcement calendar, not the reaction.
"""
from strategies.base import Strategy, hold_between_rebalances


class EarningsAnnouncementPremium(Strategy):
    name = "earnings_announcement_premium"
    lookback = 120   # the live data window must contain the last release
    extra_data = ("earnings_age",)
    params = {"window_start": 45, "window_end": 70, "min_slots": 8, "rebalance_every": 5}

    def target_weights(self, md):
        p = self.params
        c = md.close
        age = md.extra["earnings_age"].reindex(columns=c.columns)
        due = (age >= p["window_start"]) & (age <= p["window_end"])
        n = due.sum(axis=1)
        slots = n.clip(lower=p["min_slots"])          # at most 1/8 per name when few are due
        w = due.astype(float).div(slots, axis=0)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
