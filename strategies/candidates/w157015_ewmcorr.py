"""Champion with an exponentially weighted down-day correlation.

The low-correlation sleeve (70% of the book) ranks names by their correlation with the market on
the last 252 bars' down days, with every down day weighted equally. A name whose behaviour on
selloffs changed recently looks the same as one whose behaviour changed a year ago. Here down
days inside the same 252-bar window are weighted by recency, with a half-life of 126 bars, so the
latest down day counts four times as much as one 252 bars back. The window, the down-day rule
and the 63-down-day minimum are unchanged.

One change versus e126_wts_15_70_15: low-corr score is a recency-weighted correlation instead of
an equally weighted one.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class W157015EwmCorr(Strategy):
    name = "w157015_ewmcorr"
    lookback = 545
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 20,
              "reversal_window": 21, "reversal_every": 5}

    def vol_scaled(self, picks, rets, every=None):
        p = self.params
        every = int(every or p["rebalance_every"])
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, every)):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, every).ffill().fillna(0.0)

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

    @staticmethod
    def weighted_corr(x, y, window, halflife, min_count):
        """Correlation of each column of x with y over the last `window` bars, weights halving every
        `halflife` bars back. Pairs where either side is NaN are skipped."""
        k = 0.5 ** (np.arange(window) / halflife)
        ok = x.notna() & y.notna().to_numpy()[:, None]
        xv = x.where(ok, 0.0).to_numpy()
        yv = np.where(ok, y.fillna(0.0).to_numpy()[:, None], 0.0)
        m = ok.to_numpy().astype(float)
        T = len(x)

        def wsum(a):
            return np.column_stack([np.convolve(a[:, j], k)[:T] for j in range(a.shape[1])])

        n, sx, sy = wsum(m), wsum(xv), wsum(yv)
        sxx, syy, sxy = wsum(xv * xv), wsum(yv * yv), wsum(xv * yv)
        with np.errstate(invalid="ignore", divide="ignore"):
            cov = sxy / n - sx * sy / n ** 2
            var_x = sxx / n - (sx / n) ** 2
            var_y = syy / n - (sy / n) ** 2
            corr = cov / np.sqrt(var_x * var_y)
        count = ok.rolling(window, min_periods=1).sum().to_numpy()
        corr[(count < min_count) | (np.arange(T) < window - 1)[:, None]] = np.nan
        corr[~np.isfinite(corr)] = np.nan
        return pd.DataFrame(corr, index=x.index, columns=x.columns)

    def low_corr_sleeve(self, rets):
        p = self.params
        L, n = int(p["corr_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        down = mkt < -0.005
        score = self.weighted_corr(rets.where(down, axis=0), mkt.where(down), L, 126.0, L // 4)
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets, 126)

    def reversal_sleeve(self, rets):
        p = self.params
        B, W, n = int(p["lookback"]), int(p["reversal_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(B, min_periods=B).cov(mkt).div(mkt.rolling(B, min_periods=B).var(), axis=0)
        resid = rets - beta.shift(W).mul(mkt, axis=0)
        win = resid.rolling(W, min_periods=W)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets, int(p["reversal_every"]))

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        w = 0.15 * self.residual_sleeve(rets) + 0.7 * self.low_corr_sleeve(rets) + 0.15 * self.reversal_sleeve(rets)
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
