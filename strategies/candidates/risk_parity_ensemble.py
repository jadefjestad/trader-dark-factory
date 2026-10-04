"""Hypothesis (issue #53): the strategies that passed every gate are weakly correlated: residual momentum
(validation Sharpe 0.88), equal weight (0.67) and low volatility (0.38). Holding them as three sleeves
sized by inverse trailing 60-day sleeve volatility (equal risk), rebalanced monthly, gives a steadier
portfolio than any one of them, raising validation Sharpe above the champion's.

Sleeves are re-implemented here because candidates cannot import each other: residual_vol_momentum
(champion), equal weight over live names, and low_vol_tilt. Equal weight stands in for blend_ew30_residual,
whose two parts are already sleeves. Sleeve returns are estimated from held weights, before costs.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class RiskParityEnsemble(Strategy):
    name = "risk_parity_ensemble"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "top_n": 8, "vol_target": 0.10, "vol_window": 60,
              "lowvol_window": 126, "lowvol_n": 10, "risk_window": 60, "rebalance_every": 21}

    def momentum_sleeve(self, c, rets, keep):
        p = self.params
        L, S, vw = int(p["lookback"]), int(p["skip"]), int(p["vol_window"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=False, method="first")
        w = equal_weight((rank <= int(p["top_n"])) & score.notna(), slots=int(p["top_n"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return w

    def low_vol_sleeve(self, rets):
        p = self.params
        vw = int(p["lowvol_window"])
        vol = rets.rolling(vw, min_periods=vw).std()
        rank = vol.rank(axis=1, ascending=True, method="first")
        inv = (1.0 / vol).where(rank <= int(p["lowvol_n"]))
        return inv.div(inv.sum(axis=1).replace(0, np.nan), axis=0).clip(upper=0.15).fillna(0.0)

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        every = int(p["rebalance_every"])
        keep = pd.Series(rebalance_mask(c.index, every), index=c.index)
        live = c.notna()
        sleeves = [self.momentum_sleeve(c, rets, keep.values),
                   live.astype(float).div(live.sum(axis=1).replace(0, 1), axis=0),
                   self.low_vol_sleeve(rets)]
        # positions each sleeve actually holds: its rebalance-day weights carried forward
        held = [s.where(keep, axis=0).ffill().fillna(0.0) for s in sleeves]
        sleeve_ret = pd.concat([(h.shift(1) * rets).sum(axis=1, min_count=1) for h in held], axis=1)
        rw = int(p["risk_window"])
        risk = sleeve_ret.rolling(rw, min_periods=rw).std()
        inv = 1.0 / risk.where(risk > 0)
        alloc = inv.div(inv.sum(axis=1), axis=0)
        alloc[alloc.isna().any(axis=1)] = 1.0 / len(sleeves)   # equal split until every sleeve has history
        w = sum(s.fillna(0.0).mul(alloc.iloc[:, k], axis=0) for k, s in enumerate(sleeves))
        return hold_between_rebalances(w.clip(upper=0.15), every)
