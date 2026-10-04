"""Minimal Alpaca PAPER trading client. There is deliberately no way to point this at a live endpoint."""
from __future__ import annotations

import os

import requests

from factory.invariants import PAPER_URL

DATA_URL = "https://data.alpaca.markets"


class BrokerError(RuntimeError):
    pass


class PaperBroker:
    def __init__(self, key: str | None = None, secret: str | None = None, session=None):
        key = key or os.environ.get("ALPACA_API_KEY_ID")
        secret = secret or os.environ.get("ALPACA_API_SECRET_KEY")
        if not key or not secret:
            raise BrokerError("ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY not set")
        if os.environ.get("APCA_API_BASE_URL", PAPER_URL).rstrip("/") != PAPER_URL:
            raise BrokerError("APCA_API_BASE_URL is set to a non-paper endpoint; refusing to run")
        self.s = session or requests.Session()
        self.s.headers.update({"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret})

    def _req(self, method: str, path: str, **kw):
        r = self.s.request(method, PAPER_URL + path, timeout=30, **kw)
        if r.status_code >= 300:
            raise BrokerError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else None

    def account(self):
        return self._req("GET", "/v2/account")

    def clock(self):
        return self._req("GET", "/v2/clock")

    def calendar(self, start: str, end: str):
        return self._req("GET", "/v2/calendar", params={"start": start, "end": end})

    def positions(self):
        return self._req("GET", "/v2/positions")

    def open_orders(self):
        return self._req("GET", "/v2/orders", params={"status": "open", "limit": 500})

    def closed_orders(self, after: str):
        """Orders closed (filled, cancelled, ...) since `after` (ISO date), newest first."""
        return self._req("GET", "/v2/orders", params={"status": "closed", "after": after, "limit": 500})

    def portfolio_history(self, period: str = "1A"):
        return self._req("GET", "/v2/account/portfolio/history", params={"period": period, "timeframe": "1D"})

    def submit_order(self, symbol: str, qty: int, side: str, client_order_id: str):
        return self._req("POST", "/v2/orders", json={
            "symbol": symbol, "qty": str(qty), "side": side, "type": "market",
            "time_in_force": "day", "client_order_id": client_order_id,
        })

    def latest_trades(self, symbols: list[str], feed: str = "iex") -> dict:
        """{symbol: (price, timestamp)} from the market-data API (IEX is real-time on the free plan)."""
        r = self.s.get(DATA_URL + "/v2/stocks/trades/latest", params={"symbols": ",".join(symbols), "feed": feed}, timeout=30)
        if r.status_code >= 300:
            raise BrokerError(f"latest trades -> {r.status_code}: {r.text[:300]}")
        return {sym: (float(t["p"]), t["t"]) for sym, t in (r.json().get("trades") or {}).items()}
