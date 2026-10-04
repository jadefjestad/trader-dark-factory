import asyncio
import datetime as dt
import json

import pytest

from factory import config
from factory.stream import app
from factory.stream.engine import StreamEngine

T0 = dt.datetime(2026, 10, 5, 14, 0, 0, tzinfo=dt.timezone.utc)   # 10:00 New York


class FakeWS:
    def __init__(self, replies=(), stream=()):
        self.sent, self.replies, self.stream = [], list(replies), list(stream)

    async def send(self, m):
        self.sent.append(json.loads(m))

    async def recv(self):
        return json.dumps(self.replies.pop(0))

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.stream:
            await asyncio.sleep(3600)
        await asyncio.sleep(0)
        return json.dumps(self.stream.pop(0))


class FakeBroker:
    def __init__(self):
        self.orders = []

    def account(self):
        return {"account_number": "PA1", "status": "ACTIVE", "equity": "100000"}

    def positions(self):
        return []

    def clock(self):
        return {"is_open": True}

    def submit_order(self, *a):
        self.orders.append(a)


def test_authenticate_subscribes_after_success_and_fails_on_error():
    ws = FakeWS([[{"T": "success", "msg": "connected"}], [{"T": "success", "msg": "authenticated"}]])
    asyncio.run(app.authenticate(ws, "k", "s", ["AAPL"]))
    assert ws.sent[-1] == {"action": "subscribe", "trades": ["AAPL"], "quotes": ["AAPL"]}
    bad = FakeWS([[{"T": "error", "code": 402, "msg": "auth failed"}]])
    with pytest.raises(RuntimeError):
        asyncio.run(app.authenticate(bad, "k", "s", ["AAPL"]))


def test_session_feeds_engine_and_shadow_submits_nothing(monkeypatch):
    monkeypatch.setattr(app, "TICK_SECONDS", 0.01)
    lim = config.risk_limits()
    broker = FakeBroker()
    logs = []
    eng = StreamEngine(["AAPL"], 5, lambda md: {"AAPL": 0.1}, broker, lim, lim["stream"], shadow=True, log=logs.append)
    eng.start(broker.account())
    clock = {"t": T0}
    def now():
        clock["t"] += dt.timedelta(seconds=1)
        return clock["t"]
    trades = [[{"T": "t", "S": "AAPL", "p": 200.0, "s": 100, "t": (T0 + dt.timedelta(seconds=1)).isoformat()}]]

    async def go():
        stop = asyncio.Event()
        asyncio.get_running_loop().call_later(0.3, stop.set)
        await app.run_session(FakeWS(stream=trades), eng, broker, app.Health(), stop, now=now)
    asyncio.run(go())
    assert any(r["event"] == "shadow_order" for r in logs if isinstance(r, dict)), logs
    assert broker.orders == []


def test_submission_needs_flag_champion_and_executable_timeframe(monkeypatch):
    monkeypatch.delenv("STREAM_SUBMIT", raising=False)
    assert not app.submit_allowed({"timeframe": "1Day"})
    monkeypatch.setenv("STREAM_SUBMIT", "1")
    assert not app.submit_allowed(None)
    assert not app.submit_allowed({"timeframe": "5s"})       # not in executable_timeframes


def test_health_goes_stale():
    h = app.Health(max_age_s=0)
    h.beat()
    assert not h.ok()
    assert app.Health().ok() is False
