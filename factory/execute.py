"""Run the promoted (champion) strategy on Alpaca paper. Fails closed.

    python -m factory.execute --dry-run      # compute and print orders, submit nothing
    python -m factory.execute                # submit paper orders

Any data, auth, validation or risk failure exits non-zero BEFORE the first order is sent.
This needs no Claude access: GitHub Actions runs it on a schedule.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys
from pathlib import Path

import pandas as pd

from factory import config
from factory.broker import BrokerError, PaperBroker
from factory.config import ROOT
from factory.data import DataError, load_alpaca, validate
from factory.risk import RiskError, check_account, check_drawdown, check_orders, check_targets
from factory.sandbox import load_ref

CHAMPION = ROOT / "state" / "champion.json"


def load_champion():
    ch = json.loads(CHAMPION.read_text())
    if ch["ref"].endswith(".py"):
        actual = config.file_sha256(ROOT / ch["ref"])
        if actual != ch.get("code_sha256"):
            raise RiskError(f"champion code hash mismatch for {ch['ref']}")
    cls = load_ref(ch["ref"])
    if cls.timeframe != "1Day":
        raise RiskError(f"champion timeframe {cls.timeframe} has no executor yet (daily only)")
    return ch, cls(**ch.get("params", {}))


def plan_orders(targets: dict, positions: dict, prices: dict, equity: float, min_notional: float) -> list:
    orders = []
    for sym in sorted(set(targets) | set(positions)):
        if sym not in targets:
            continue  # positions outside the strategy universe are left alone
        px = prices[sym]
        want = math.floor(targets[sym] * equity / px) if targets[sym] > 0 else 0
        have = int(positions.get(sym, 0))
        delta = want - have
        if delta == 0 or abs(delta) * px < min_notional:
            continue
        orders.append({"symbol": sym, "qty": abs(delta), "side": "buy" if delta > 0 else "sell"})
    return sorted(orders, key=lambda o: o["side"] != "sell")  # sells first


def run(dry_run: bool, out_dir: Path) -> dict:
    limits = config.risk_limits()
    cfg = config.evaluation()
    symbols = config.universe()["symbols"]
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    record = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "dry_run": dry_run, "status": "started", "orders": [], "submitted": []}

    if not limits.get("trading_enabled", False):
        record["status"] = "halted: trading_enabled is false"
        return record

    broker = PaperBroker()
    acct = broker.account()
    check_account(acct, limits)
    equity = float(acct["equity"])
    hist = broker.portfolio_history().get("equity") or []
    record["drawdown"] = round(check_drawdown(equity, hist, limits), 4)

    clock = broker.clock()
    if not clock.get("is_open") and not dry_run:
        record["status"] = "skipped: market closed"
        return record
    if broker.open_orders():
        raise RiskError("open orders exist from an earlier run; refusing to add more")

    ch, strat = load_champion()
    record["champion"] = {k: ch.get(k) for k in ("name", "ref", "experiment_id")}

    cal = broker.calendar((today - pd.Timedelta(days=14)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    sessions = [pd.Timestamp(d["date"]) for d in cal if pd.Timestamp(d["date"]) < today]
    if not sessions:
        raise DataError("no previous trading session in calendar")
    prev_session = sessions[-1]

    start = (today - pd.Timedelta(days=int(strat.lookback * 1.6) + 10)).strftime("%Y-%m-%d")
    d = cfg["data"]
    md = load_alpaca(symbols, start, "latest", "1Day", feed=d["historical_feed"],
                     fallback_feed=d.get("fallback_feed"), adjustment=d["adjustment"], use_cache=False)
    md = md.slice(None, prev_session)                     # completed sessions only, no partial bar
    validate(md, symbols)
    last = md.index[-1]
    if last != prev_session:
        raise DataError(f"latest bar {last.date()} != previous session {prev_session.date()}")
    if (today - last).days > limits["max_data_staleness_days"]:
        raise DataError(f"data is {(today - last).days} days old")
    if md.close.iloc[-1].isna().any():
        raise DataError("missing closes on the latest bar")

    w = strat.target_weights(md).reindex(columns=symbols).iloc[-1].fillna(0.0)
    targets = {s: float(w[s]) for s in symbols}
    check_targets(targets, symbols, limits)
    prices = {s: float(md.close[s].iloc[-1]) for s in symbols}
    positions = {p["symbol"]: float(p["qty"]) for p in broker.positions()}
    orders = plan_orders(targets, positions, prices, equity, limits["min_order_notional"])
    check_orders(orders, prices, equity, limits)
    record.update({"equity": equity, "signal_bar": str(last.date()), "targets": targets, "orders": orders,
                   "data_source": md.source})

    if dry_run:
        record["status"] = "dry run: no orders submitted"
        return record

    run_id = os.environ.get("GITHUB_RUN_ID", dt.datetime.now(dt.timezone.utc).strftime("%H%M%S"))
    for o in orders:
        coid = f"tdf-{today:%Y%m%d}-{run_id}-{o['symbol']}-{o['side']}"
        resp = broker.submit_order(o["symbol"], o["qty"], o["side"], coid)   # raises on failure: stop here
        record["submitted"].append({"client_order_id": coid, "id": resp.get("id"), **o})
    record["status"] = f"submitted {len(orders)} orders"
    return record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "experiments" / "executions"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    code = 0
    try:
        record = run(a.dry_run, out)
    except Exception as e:  # anything unexpected also means: stop, no further orders
        record = {"status": f"NO ORDERS: {type(e).__name__}: {e}",
                  "started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
        code = 2
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    (out / f"{stamp}.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
    print(json.dumps(record, indent=2, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
