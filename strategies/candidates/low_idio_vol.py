"""Hypothesis: the idiosyncratic-volatility puzzle (Ang, Hodrick, Xing and Zhang 2006) says stocks
with low stock-specific volatility earn higher risk-adjusted returns than high-idio-vol stocks.
low_vol_tilt (total volatility) and low_beta / low_correlation (market exposure) already passed;
ranking on residual volatility alone isolates the stock-specific part. Holding the 8 names with the
lowest 252-day residual volatility, equal weight scaled to a 10% vol target and rebalanced monthly,
should give a validation Sharpe near low_correlation (1.12) with a different set of names.

One change versus low_correlation: rank on 252-day residual (beta-adjusted) volatility instead of
correlation to the equal-weight universe. Row t uses closes up to bar t only.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowIdioVol(Strategy):
    name = "low_idio_vol"
    lookback = 520
    params = {"beta_window": 252, "idio_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        B, L, n, every = int(p["beta_window"]), int(p["idio_window"]), int(p["top_n"]), int(p["rebalance_every"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(B, min_periods=B).cov(mkt).div(mkt.rolling(B, min_periods=B).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        score = resid.rolling(L, min_periods=L).std()
        rank = score.rank(axis=1, ascending=True, method="first")
        w = equal_weight((rank <= n) & score.notna(), slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, every)):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        w = hold_between_rebalances(w, every).ffill().fillna(0.0)
        keep = rebalance_mask(w.index, every)
        return w.where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
