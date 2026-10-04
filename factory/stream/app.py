"""The streamer process (issue #69): Alpaca IEX websocket in, paper orders (or shadow logs) out.

    python -m factory.stream.app            # what deploy/streamer/Dockerfile runs

It runs with no Claude involvement. The strategy is the one in state/champion_stream.json, chosen by the
evaluator and promoted by merge; with no such file it runs a flat strategy in shadow mode as a smoke
test of the feed, bars, logging and health check. Orders are submitted only when STREAM_SUBMIT=1 and
the champion's timeframe is in the protected executable_timeframes; otherwise everything is shadow.
Any failure at start (keys, non-paper account, limits) exits before the first message is read.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from factory import config
from factory.config import ROOT
from factory.stream.engine import StreamEngine

STREAM_URL = "wss://stream.data.alpaca.markets/v2/iex"
CHAMPION_STREAM = ROOT / "state" / "champion_stream.json"
TICK_SECONDS = 1.0
SYNC_SECONDS = 60          # positions, equity and the market clock are refreshed this often


def load_strategy() -> tuple[dict | None, object]:
    """(champion or None, decide function). The strategy always runs in the credential-free sandbox."""
    if not CHAMPION_STREAM.exists():
        return None, lambda md: {}
    from factory import runner
    ch = json.loads(CHAMPION_STREAM.read_text())
    if ch["ref"].endswith(".py") and config.file_sha256(ROOT / ch["ref"]) != ch.get("code_sha256"):
        raise RuntimeError(f"stream champion code hash mismatch for {ch['ref']}")

    def decide(md):
        w = runner.run(ch["ref"], md, [{"params": ch.get("params")}], timeout=20)[0]
        last = w.iloc[-1]
        if last.isna().all():
            raise ValueError("hold row")   # the engine treats this as no decision
        return last.to_dict()
    return ch, decide


def submit_allowed(champion: dict | None) -> bool:
    executable = config.evaluation()["promotion"]["executable_timeframes"]
    return (os.environ.get("STREAM_SUBMIT") == "1" and champion is not None
            and champion.get("timeframe") in executable)


class JsonLog:
    def __init__(self, directory: Path):
        self.dir = directory
        self.dir.mkdir(parents=True, exist_ok=True)

    def __call__(self, rec: dict) -> None:
        day = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d")
        with open(self.dir / f"stream-{day}.jsonl", "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")


class Health:
    """Last successful tick; /healthz answers 200 only while ticks are recent."""
    def __init__(self, max_age_s: float = 30):
        self.last = None
        self.max_age = max_age_s

    def beat(self):
        self.last = dt.datetime.now(dt.timezone.utc)

    def ok(self) -> bool:
        return self.last is not None and (dt.datetime.now(dt.timezone.utc) - self.last).total_seconds() < self.max_age

    def serve(self, port: int) -> None:
        health = self

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200 if health.ok() else 503)
                self.end_headers()

            def log_message(self, *a):
                pass
        threading.Thread(target=HTTPServer(("0.0.0.0", port), H).serve_forever, daemon=True).start()


async def authenticate(ws, key: str, secret: str, symbols: list[str]) -> None:
    await ws.send(json.dumps({"action": "auth", "key": key, "secret": secret}))
    for _ in range(3):
        msgs = json.loads(await ws.recv())
        if any(m.get("T") == "error" for m in msgs):
            raise RuntimeError(f"stream auth failed: {msgs}")
        if any(m.get("T") == "success" and m.get("msg") == "authenticated" for m in msgs):
            break
    else:
        raise RuntimeError("stream never confirmed authentication")
    await ws.send(json.dumps({"action": "subscribe", "trades": symbols, "quotes": symbols}))


async def run_session(ws, engine: StreamEngine, broker, health: Health, stop: asyncio.Event,
                      now=lambda: dt.datetime.now(dt.timezone.utc)) -> None:
    """Pump messages into the engine and tick it, until `stop` is set or the socket closes."""
    state = {"positions": {}, "equity": 0.0, "open": False, "synced": None}

    def sync():
        acct = broker.account()
        state["equity"] = float(acct["equity"])
        state["positions"] = {p["symbol"]: int(float(p["qty"])) for p in broker.positions()}
        state["open"] = bool(broker.clock().get("is_open"))
        state["synced"] = now()

    async def reader():
        async for raw in ws:
            received = now()
            for m in json.loads(raw):
                engine.on_message(m, received)

    task = asyncio.create_task(reader())
    try:
        while not stop.is_set() and not task.done():
            t = now()
            if state["synced"] is None or (t - state["synced"]).total_seconds() >= SYNC_SECONDS:
                sync()
            engine.tick(t, state["positions"], state["equity"], state["open"])
            health.beat()
            try:
                await asyncio.wait_for(stop.wait(), TICK_SECONDS)
            except asyncio.TimeoutError:
                pass
    finally:
        task.cancel()
    if task.done() and not task.cancelled() and task.exception():
        raise task.exception()     # a broken feed ends the session; the platform restarts and re-checks


def main() -> int:
    import websockets

    from factory.broker import PaperBroker

    limits = config.risk_limits()
    champion, decide = load_strategy()
    symbols = (champion or {}).get("symbols") or config.universe()["symbols"][:10]
    seconds = int((champion or {}).get("bar_seconds", 60))
    log = JsonLog(Path(os.environ.get("STREAM_LOG_DIR", "/var/log/stream")))
    broker = PaperBroker()
    engine = StreamEngine(symbols, seconds, decide, broker, limits, limits["stream"],
                          shadow=not submit_allowed(champion), log=log)
    engine.start(broker.account())               # paper account check; raises before any message is read
    health = Health()
    health.serve(int(os.environ.get("PORT", "8080")))
    log({"event": "start", "champion": (champion or {}).get("ref"), "shadow": engine.shadow, "symbols": symbols})

    async def go():
        stop = asyncio.Event()
        async with websockets.connect(STREAM_URL) as ws:
            await authenticate(ws, os.environ["ALPACA_API_KEY_ID"], os.environ["ALPACA_API_SECRET_KEY"], symbols)
            await run_session(ws, engine, broker, health, stop)
    asyncio.run(go())
    return 1   # the session ended (socket closed): exit non-zero so the platform restarts and re-checks


if __name__ == "__main__":
    sys.exit(main())
