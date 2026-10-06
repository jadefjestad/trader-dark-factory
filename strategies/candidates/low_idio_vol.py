"""Hypothesis: stocks with high idiosyncratic volatility earn low future returns (Ang, Hodrick, Xing
and Zhang 2006, "The cross-section of volatility and expected returns"). Among large caps, holding the
eight stocks with the lowest standard deviation of daily returns after removing their 252-day market
beta, measured over the last 63 days, sized to a 10% volatility target and rebalanced monthly, should
earn a positive validation Sharpe. This ranks on stock-specific risk only, so it differs from
low_beta (market co-movement) and low_vol_tilt (total volatility).

One change versus low_beta: the ranking signal is trailing idiosyncratic volatility, lowest first.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowIdioVol(Strategy):
    name = "low_idio_vol"
    lookback = 340   # beta (252) + idiosyncratic window (63) + margin
    params = {"beta_window": 252, "idio_window": 63, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        L = int(p["beta_window"])
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        iw = int(p["idio_window"])
        score = resid.rolling(iw, min_periods=iw).std()
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
