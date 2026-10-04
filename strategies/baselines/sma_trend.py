from strategies.base import Strategy


class SmaTrend(Strategy):
    """Hold each stock at 1/N while its fast SMA is above its slow SMA."""
    name = "sma_trend"
    lookback = 220
    params = {"fast": 50, "slow": 200}

    def target_weights(self, md):
        c = md.close
        fast = c.rolling(int(self.params["fast"])).mean()
        slow = c.rolling(int(self.params["slow"])).mean()
        return (fast > slow).astype(float) / c.shape[1]
