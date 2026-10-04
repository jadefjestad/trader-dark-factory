"""Run the promoted (champion) strategy on Alpaca paper. Fails closed.

    python -m factory.execute --dry-run      # compute and print orders, submit nothing
    python -m factory.execute                # submit paper orders

Any data, auth, validation or risk failure exits non-zero BEFORE the first order is sent. If a
submission fails part-way, the run record keeps every order already accepted.
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

import numpy as np
import pandas as pd

from factory import config, runner
from factory.broker import PaperBroker
from factory.config import ROOT
from factory.data import DataError, load_alpaca, validate
from factory.risk import RiskError, check_account, check_drawdown, check_orders, check_targets

CHAMPION = ROOT / "state" / "champion.json"


def load_champion() -> tuple[dict, dict]:
    ch = json.loads(CHAMPION.read_text())
    if ch["ref"].endswith(".py"):
        path = ROOT / ch["ref"]
        if not path.is_file() or config.file_sha256(path) != ch.get("code_sha256"):
            raise RiskError(f"champion code missing or hash mismatch for {ch['ref']}")
    meta = runner.describe(ch["ref"])
    if meta["timeframe"] != "1Day":
        raise RiskError(f"champion timeframe {meta['timeframe']} has no executor yet (daily only)")
    return ch, meta


def decide(weights: pd.DataFrame, symbols: list[str]) -> tuple[dict | None, bool]:
    """Return (targets, is_hold_day). An all-NaN last row means hold: use the latest decision row."""
    last = weights.iloc[-1]
    if last.isna().all():
        rows = weights.dropna(how="all")
        if rows.empty:
            return None, True
        last = rows.iloc[-1]
        hold = True
    else:
        hold = False
    if last.isna().any():
        raise RiskError(f"strategy returned NaN weights for {list(last[last.isna()].index)}")
    return {s: float(last[s]) for s in symbols}, hold


def plan_orders(targets: dict, positions: dict, prices: dict, equity: float, min_notional: float,
                tolerance: float = 0.0) -> list:
    orders = []
    for sym in sorted(targets):
        px = prices[sym]
        have = int(positions.get(sym, 0))
        if tolerance and abs(have * px / equity - targets[sym]) <= tolerance:
            continue
        want = math.floor(targets[sym] * equity / px) if targets[sym] > 0 else 0
        delta = want - have
        if delta == 0 or abs(delta) * px < min_notional:
            continue
        orders.append({"symbol": sym, "qty": abs(delta), "side": "buy" if delta > 0 else "sell"})
    return sorted(orders, key=lambda o: o["side"] != "sell")  # sells first


def latest_prices(broker, symbols, closes: dict, limits: dict) -> dict:
    trades = broker.latest_trades(symbols)
    now = pd.Timestamp.now(tz="UTC")
    prices = {}
    for s in symbols:
        if s not in trades:
            raise DataError(f"no latest trade for {s}")
        px, ts = trades[s]
        age = (now - pd.Timestamp(ts)).total_seconds() / 60
        if age > limits["max_quote_age_minutes"]:
            raise DataError(f"latest trade for {s} is {age:.0f} minutes old")
        if not np.isfinite(px) or abs(px / closes[s] - 1) > limits["max_price_gap"]:
            raise DataError(f"latest trade {px} for {s} is implausible vs last close {closes[s]}")
        prices[s] = px
    return prices


def run(dry_run: bool, record: dict) -> None:
    limits = config.risk_limits()
    cfg = config.evaluation()
    symbols = config.universe()["symbols"]
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)

    if not limits.get("trading_enabled", False):
        record["status"] = "halted: trading_enabled is false"
        return

    broker = PaperBroker()
    acct = broker.account()
    check_account(acct, limits)
    equity = float(acct["equity"])
    hist = broker.portfolio_history().get("equity") or []
    record["drawdown"] = round(check_drawdown(equity, hist, limits), 4)

    clock = broker.clock()
    if not clock.get("is_open") and not dry_run:
        record["status"] = "skipped: market closed"
        return
    if broker.open_orders():
        raise RiskError("open orders exist from an earlier run; refusing to add more")
    positions = {p["symbol"]: float(p["qty"]) for p in broker.positions()}
    foreign = sorted(set(positions) - set(symbols))
    if foreign:
        raise RiskError(f"positions outside the strategy universe: {foreign}; close them by hand first")
    if any(q < 0 for q in positions.values()) and not limits["allow_short"]:
        raise RiskError("short positions exist while shorting is disabled")

    ch, meta = load_champion()
    record["champion"] = {k: ch.get(k) for k in ("name", "ref", "experiment_id")}

    cal = broker.calendar((today - pd.Timedelta(days=14)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    sessions = [pd.Timestamp(d["date"]) for d in cal if pd.Timestamp(d["date"]) < today]
    if not sessions:
        raise DataError("no previous trading session in calendar")
    prev_session = sessions[-1]

    start = (today - pd.Timedelta(days=int(meta["lookback"] * 1.6) + 30)).strftime("%Y-%m-%d")
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
    if len(md.index) < meta["lookback"]:
        raise DataError(f"{len(md.index)} bars < strategy lookback {meta['lookback']}")
    if md.close.iloc[-1].isna().any():
        raise DataError("missing closes on the latest bar")

    weights = runner.run(ch["ref"], md, [{"params": ch.get("params"), "rows": None}])[0]
    targets, hold = decide(weights, symbols)
    record.update({"signal_bar": str(last.date()), "hold_day": hold, "equity": equity, "data_source": md.source})
    if targets is None:
        record["status"] = "no decision yet: strategy has not produced a target"
        return
    check_targets(targets, symbols, limits)

    closes = {s: float(md.close[s].iloc[-1]) for s in symbols}
    prices = latest_prices(broker, symbols, closes, limits)
    sizing_equity = equity * (1 - limits["cash_buffer"])
    tol = limits["hold_rebalance_tolerance"] if hold else 0.0
    orders = plan_orders(targets, positions, prices, sizing_equity, limits["min_order_notional"], tol)
    worst = {s: p * (1 + limits["price_buffer"]) for s, p in prices.items()}
    check_orders(orders, worst, equity, limits)
    buys = sum(o["qty"] * worst[o["symbol"]] for o in orders if o["side"] == "buy")
    sells = sum(o["qty"] * prices[o["symbol"]] * (1 - limits["price_buffer"]) for o in orders if o["side"] == "sell")
    if buys > float(acct["cash"]) + sells:
        raise RiskError(f"buys ${buys:,.0f} exceed cash ${float(acct['cash']):,.0f} plus sells ${sells:,.0f}")
    record.update({"targets": targets, "prices": prices, "orders": orders})

    if dry_run:
        record["status"] = "dry run: no orders submitted"
        return

    run_id = os.environ.get("GITHUB_RUN_ID", dt.datetime.now(dt.timezone.utc).strftime("%H%M%S"))
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    for o in orders:
        coid = f"tdf-{today:%Y%m%d}-{run_id}-{attempt}-{o['symbol']}-{o['side']}"
        record["pending"] = {"client_order_id": coid, **o}            # outcome unknown if the call raises
        resp = broker.submit_order(o["symbol"], o["qty"], o["side"], coid)
        record["submitted"].append({"client_order_id": coid, "id": resp.get("id"), **o})
        record.pop("pending")
    record["status"] = f"submitted {len(orders)} orders"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "experiments" / "executions"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    record = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "dry_run": a.dry_run, "status": "started", "orders": [], "submitted": []}
    code = 0
    try:
        run(a.dry_run, record)
    except Exception as e:  # anything unexpected also means: stop, no further orders
        n = len(record["submitted"])
        prefix = "NO ORDERS" if n == 0 and "pending" not in record else f"STOPPED AFTER {n} ORDER(S)"
        record["status"] = f"{prefix}: {type(e).__name__}: {e}"
        code = 2
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    (out / f"{stamp}.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
    print(json.dumps(record, indent=2, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
