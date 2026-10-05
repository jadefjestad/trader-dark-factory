"""Run each paper fund's strategy on its own Alpaca paper account. Fails closed, per fund.

    python -m factory.execute --dry-run      # compute and print orders, submit nothing
    python -m factory.execute                # submit paper orders for every fund with keys
    python -m factory.execute --fund 3       # one fund only

Funds and their strategies are in state/funds.yaml (factory/funds.py). Any data, auth, validation or
risk failure in a fund stops that fund BEFORE its first order and never touches the other funds; the
run exits non-zero if any fund failed. If a submission fails part-way, the fund's run record keeps
every order already accepted. This needs no Claude access: GitHub Actions runs it on a schedule.
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

from factory import config, extras, funds, runner
from factory.broker import PaperBroker
from factory.config import ROOT
from factory.data import DataError, load_alpaca, validate
from factory.risk import RiskError, check_account, check_drawdown, check_orders, check_targets

CHAMPION = ROOT / "state" / "champion.json"


def load_champion() -> tuple[dict, dict]:
    return load_strategy(funds.Fund(1, "champion", "", "champion"))


def load_strategy(fund) -> tuple[dict, dict]:
    try:
        ch = funds.strategy(fund, CHAMPION)
    except funds.FundError as e:
        raise RiskError(str(e)) from None
    meta = runner.describe(ch["ref"])
    if meta["timeframe"] != "1Day":
        raise RiskError(f"{ch['name']} timeframe {meta['timeframe']} has no executor yet (daily only)")
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
        # the drift tolerance only skips resizing a held position; opening or closing one always trades
        if tolerance and have != 0 and targets[sym] > 0 and abs(have * px / equity - targets[sym]) <= tolerance:
            continue
        want = math.floor(targets[sym] * equity / px) if targets[sym] > 0 else 0
        delta = want - have
        if delta == 0 or abs(delta) * px < min_notional:
            continue
        orders.append({"symbol": sym, "qty": abs(delta), "side": "buy" if delta > 0 else "sell"})
    return sorted(orders, key=lambda o: o["side"] != "sell")  # sells first


def latest_prices(broker, symbols, closes: dict, limits: dict, allow_stale: bool = False) -> dict:
    trades = broker.latest_trades(symbols)
    now = pd.Timestamp.now(tz="UTC")
    prices = {}
    for s in symbols:
        if s not in trades:
            raise DataError(f"no latest trade for {s}")
        px, ts = trades[s]
        age = (now - pd.Timestamp(ts)).total_seconds() / 60
        if age > limits["max_quote_age_minutes"] and not allow_stale:
            raise DataError(f"latest trade for {s} is {age:.0f} minutes old")
        if not np.isfinite(px) or abs(px / closes[s] - 1) > limits["max_price_gap"]:
            raise DataError(f"latest trade {px} for {s} is implausible vs last close {closes[s]}")
        prices[s] = px
    return prices


def run(dry_run: bool, record: dict, fund=None, creds=None, shared=None) -> None:
    """One fund's run. `shared` carries bars and the accounts already seen between the funds of one run."""
    fund = fund or funds.Fund(1, "champion", "", "champion")
    shared = {} if shared is None else shared
    md_cache, seen = shared.setdefault("bars", {}), shared.setdefault("accounts", {})
    limits = config.risk_limits()
    cfg = config.evaluation()
    symbols = config.universe()["symbols"]
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)

    if not limits.get("trading_enabled", False):
        record["status"] = "halted: trading_enabled is false"
        return

    broker = PaperBroker(*creds) if creds else PaperBroker()
    acct = broker.account()
    check_account(acct, limits)
    other = seen.setdefault(acct.get("account_number"), fund.number)
    if other != fund.number:
        raise RiskError(f"fund {fund.number} has the same paper account as fund {other}; give each fund its own keys")
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

    ch, meta = load_strategy(fund)
    record["strategy"] = {k: ch.get(k) for k in ("name", "ref", "experiment_id")}
    if ch.get("champion"):
        record["champion"] = record["strategy"]

    cal = broker.calendar((today - pd.Timedelta(days=14)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    sessions = [pd.Timestamp(d["date"]) for d in cal if pd.Timestamp(d["date"]) < today]
    if not sessions:
        raise DataError("no previous trading session in calendar")
    prev_session = sessions[-1]

    start = (today - pd.Timedelta(days=int(meta["lookback"] * 1.6) + 30)).strftime("%Y-%m-%d")
    d = cfg["data"]
    if start not in md_cache:   # funds share bars within one run; a failed load is not cached
        md_cache[start] = load_alpaca(symbols, start, "latest", "1Day", feed=d["historical_feed"],
                                      fallback_feed=d.get("fallback_feed"), adjustment=d["adjustment"], use_cache=False)
    md = md_cache[start]
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
    md = extras.attach(md, meta.get("extra_data"), "alpaca")   # raises DataError: no orders without the data

    weights = runner.run(ch["ref"], md, [{"params": ch.get("params"), "rows": None}])[0]
    targets, hold = decide(weights, symbols)
    record.update({"signal_bar": str(last.date()), "hold_day": hold, "equity": equity, "data_source": md.source})
    if targets is None:
        record["status"] = "no decision yet: strategy has not produced a target"
        return
    check_targets(targets, symbols, limits)

    closes = {s: float(md.close[s].iloc[-1]) for s in symbols}
    # a dry run outside market hours previews orders on the last available trades
    stale_ok = dry_run and not clock.get("is_open")
    prices = latest_prices(broker, symbols, closes, limits, allow_stale=stale_ok)
    if stale_ok:
        record["note"] = "market closed: preview priced on the last available trades"
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
        coid = f"tdf-f{fund.number}-{today:%Y%m%d}-{run_id}-{attempt}-{o['symbol']}-{o['side']}"
        record["pending"] = {"client_order_id": coid, **o}            # outcome unknown if the call raises
        resp = broker.submit_order(o["symbol"], o["qty"], o["side"], coid)
        record["submitted"].append({"client_order_id": coid, "id": resp.get("id"), **o})
        record.pop("pending")
    record["status"] = f"submitted {len(orders)} orders"


def run_fund(fund, creds, dry_run: bool, out: Path, shared: dict) -> int:
    record = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "fund": fund.number,
              "fund_name": fund.label, "dry_run": dry_run, "status": "started", "orders": [], "submitted": []}
    if creds is None:   # not funded yet: nothing to record on the ledger
        print(f"fund {fund.number} skipped: no secrets ALPACA_FUND_{fund.number}_KEY_ID / ALPACA_FUND_{fund.number}_SECRET_KEY")
        return 0
    code = 0
    try:
        run(dry_run, record, fund, creds, shared)
    except Exception as e:  # anything unexpected also means: stop this fund, no further orders
        n = len(record["submitted"])
        prefix = "NO ORDERS" if n == 0 and "pending" not in record else f"STOPPED AFTER {n} ORDER(S)"
        record["status"] = f"{prefix}: {type(e).__name__}: {e}"
        code = 2
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    (out / f"{stamp}-f{fund.number}.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
    print(json.dumps(record, indent=2, default=str))
    return code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fund", type=int, help="run only this fund number")
    ap.add_argument("--out", default=str(ROOT / "experiments" / "executions"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        all_funds = [f for f in funds.load() if a.fund is None or f.number == a.fund]
    except Exception as e:
        all_funds, err = [], f"{type(e).__name__}: {e}"
    else:
        err = None if all_funds else f"no fund numbered {a.fund}"
    keyed = [(f, funds.credentials(f.number)) for f in all_funds]
    if err is None and not any(c for _, c in keyed):
        err = "no fund has Alpaca paper keys"
    if err:   # nothing ran: record it and fail visibly
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        rec = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "dry_run": a.dry_run,
               "status": f"NO ORDERS: {err}", "orders": [], "submitted": []}
        (out / f"{stamp}.json").write_text(json.dumps(rec, indent=2) + "\n")
        print(json.dumps(rec, indent=2))
        return 2
    shared: dict = {}
    codes = [run_fund(f, c, a.dry_run, out, shared) for f, c in keyed]
    return max(codes)


if __name__ == "__main__":
    sys.exit(main())
