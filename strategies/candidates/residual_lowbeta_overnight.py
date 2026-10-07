"""Hypothesis: the 50/50 residual-momentum plus low-beta blend (PR #126: validation Sharpe 1.05, holdout
about 1.7) and overnight momentum (PR #115: validation 0.84) rank on three unrelated traits. Splitting
the book into equal thirds (residual momentum, low beta, overnight momentum), each sleeve unchanged at
a 10% vol target and rebalanced monthly, should diversify further and lift the validation Sharpe.

One change versus residual_lowbeta_blend: a third sleeve of overnight momentum, with equal thirds.
Row t uses opens and closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualLowBetaOvernight(Strategy):
    name = "residual_lowbeta_overnight"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "beta_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60, "overnight_window": 252}

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

    def residual_sleeve(self, rets):
        p = self.params
        L, S, n = int(p["lookback"]), int(p["skip"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=False)
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def low_beta_sleeve(self, rets):
        p = self.params
        L, n = int(p["beta_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        score = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def overnight_sleeve(self, md, rets):
        p = self.params
        win, n = int(p["overnight_window"]), int(p["top_n"])
        score = np.log(md.open / md.close.shift(1)).rolling(win, min_periods=win).sum()
        rank = score.rank(axis=1, ascending=False, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        w = (self.residual_sleeve(rets) + self.low_beta_sleeve(rets) + self.overnight_sleeve(md, rets)) / 3
        return hold_between_rebalances(w, int(p["rebalance_every"]))
