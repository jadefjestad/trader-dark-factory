"""Run the intraday (15-minute) paper funds once per completed bar through the session. Fails closed, per fund.

    python -m factory.intraday --once --dry-run       # one decision for every intraday fund now, no orders
    python -m factory.intraday --max-minutes 340      # loop through the session (GitHub Actions)

A fund is intraday when its strategy's timeframe is not 1Day (state/funds.yaml); factory.execute runs the
daily ones. Each bar, for each intraday fund: check the paper account, fetch the last days of IEX bars with
the fund's own keys, keep completed bars only, run the strategy in the sandbox, and trade to the newest
row's weights. Everything the daily executor checks is checked here too (protected/risk_limits.yaml, with
the `intraday:` section on top). The book is flat by the close: decisions on the session's last two bars
are zero, exactly as the backtester forces them, and a fund 3% down on the day flattens and stops.

Any data, auth, validation or risk failure stops that fund for that bar BEFORE its first order and never
touches the other funds. Each order's client id names the fund and the bar, so a second run on the same
bar can never double an order. Needs no Claude access.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

from factory import config, extras, funds, runner
from factory.broker import PaperBroker
from factory.config import ROOT
from factory.data import DataError, MarketData, load_alpaca, validate
from factory.execute import CHAMPION, decide, latest_prices, plan_orders
from factory.risk import RiskError, check_account, check_drawdown, check_orders, check_targets

NY = "America/New_York"


def bar_minutes(timeframe: str) -> int:
    if not timeframe.endswith("Min") or not timeframe[:-3].isdigit():
        raise RiskError(f"timeframe {timeframe} is not an intraday bar size")
    return int(timeframe[:-3])


def completed_bars(md: MarketData, now: pd.Timestamp, minutes: int, max_missing: int) -> MarketData:
    """Bars that ended by `now`, with at most `max_missing` trailing gaps per symbol filled from the last price.
    IEX carries ~5% of volume, so a quiet name can lack a 15-minute bar; a longer gap means the data is bad."""
    md = md.slice(None, now - pd.Timedelta(minutes=minutes))
    if len(md.index) == 0:
        raise DataError("no completed bars")
    px = {f: getattr(md, f).ffill(limit=max_missing) for f in ("open", "high", "low", "close")}
    last = md.close.iloc[-(max_missing + 1):]
    dead = [s for s in md.symbols if last[s].isna().all()]
    if dead:
        raise DataError(f"no bar in the last {max_missing + 1} for {dead}")
    return MarketData(px["open"], px["high"], px["low"], px["close"], md.volume.fillna(0.0),
                      timeframe=md.timeframe, source=md.source)


def run(dry_run: bool, record: dict, fund, creds, shared: dict, now: pd.Timestamp | None = None) -> None:
    """One fund, one bar. `shared` carries bars, accounts and per-day stops between funds and bars of one job."""
    now = now or pd.Timestamp.now(tz=NY)
    limits = config.risk_limits()
    il = limits["intraday"]
    symbols = config.universe()["symbols"]
    if not limits.get("trading_enabled", False):
        record["status"] = "halted: trading_enabled is false"
        return

    broker = PaperBroker(*creds)
    acct = broker.account()
    check_account(acct, limits)
    other = shared.setdefault("accounts", {}).setdefault(acct.get("account_number"), fund.number)
    if other != fund.number:
        raise RiskError(f"fund {fund.number} has the same paper account as fund {other}; give each fund its own keys")
    equity = float(acct["equity"])
    hist = broker.portfolio_history().get("equity") or []
    record["drawdown"] = round(check_drawdown(equity, hist, limits), 4)

    clock = broker.clock()
    if not clock.get("is_open") and not dry_run:
        record["status"] = "skipped: market closed"
        return
    close_at = pd.Timestamp(clock["next_close"]).tz_convert(NY) if clock.get("next_close") else None

    try:
        s = funds.strategy(fund, CHAMPION)
    except funds.FundError as e:
        raise RiskError(str(e)) from None
    meta = runner.describe(s["ref"])
    minutes = bar_minutes(meta["timeframe"])
    record["strategy"] = {k: s.get(k) for k in ("name", "ref", "experiment_id")}

    last_eq = float(acct.get("last_equity") or equity)
    day_loss = 1 - equity / last_eq if last_eq > 0 else 0.0
    stopped = shared.setdefault("stopped", {})
    if day_loss > il["max_daily_loss"]:
        stopped[(fund.number, now.date())] = f"down {day_loss:.1%} on the day"
    stop = stopped.get((fund.number, now.date()))
    bar_len = pd.Timedelta(minutes=minutes)
    flat_bars = int(il["flatten_bars_before_close"])
    expected = now.floor(f"{minutes}min") - bar_len          # the bar that has just completed
    # the backtester zeroes a decision whose fill bar is the session's last; from then on the book is flat,
    # decided without fresh bars so a data failure can never keep a position overnight
    if close_at is not None and expected + bar_len * flat_bars >= close_at:
        stop = stop or "end of session"

    if broker.open_orders():
        if not stop:
            raise RiskError("open orders exist from an earlier bar; refusing to add more")
        broker.cancel_open_orders()   # flattening: clear what is pending first
        time.sleep(2)
    positions = {p["symbol"]: float(p["qty"]) for p in broker.positions()}
    foreign = sorted(set(positions) - set(symbols))
    if foreign:
        raise RiskError(f"positions outside the strategy universe: {foreign}; close them by hand first")
    if any(q < 0 for q in positions.values()) and not limits["allow_short"]:
        raise RiskError("short positions exist while shorting is disabled")

    signal, closes = None, None
    if stop:
        targets, hold = {sym: 0.0 for sym in symbols}, False
        record["note"] = f"flat: {stop}"
    else:
        key = (meta["timeframe"], expected)
        cache = shared.setdefault("bars", {})
        if key not in cache:    # each fund fetches with its own keys; bars are shared once loaded, failures are not
            start = (now - pd.Timedelta(days=int(il["history_days"]))).strftime("%Y-%m-%d")
            cache[key] = load_alpaca(symbols, start, now.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
                                     meta["timeframe"], feed=il["feed"], fallback_feed=None, adjustment="all",
                                     use_cache=False, creds=creds)
        md = completed_bars(cache[key], now, minutes, int(il["max_missing_bars"]))
        validate(md, symbols)
        signal = md.index[-1]
        age = (now - (signal + bar_len)).total_seconds() / 60
        if age > il["max_bar_age_minutes"]:
            raise DataError(f"newest completed bar {signal} ended {age:.0f} minutes ago")
        if len(md.index) < meta["lookback"]:
            raise DataError(f"{len(md.index)} bars < strategy lookback {meta['lookback']}")
        md = extras.attach(md, meta.get("extra_data"), "alpaca")
        weights = runner.run(s["ref"], md, [{"params": s.get("params"), "rows": None}])[0]
        targets, hold = decide(weights, symbols)
        if hold and targets is not None:
            last_row = weights.dropna(how="all").index[-1]
            if last_row.date() != signal.date():   # yesterday's book was flattened overnight: holding it means flat
                targets = {sym: 0.0 for sym in symbols}
        if targets is None:
            targets, hold = {sym: 0.0 for sym in symbols}, False
        closes = {sym: float(md.close[sym].iloc[-1]) for sym in symbols}
    record.update({"signal_bar": str(signal) if signal is not None else None, "hold_day": hold, "equity": equity})
    check_targets(targets, symbols, limits)

    if closes is None:   # flattening without fresh bars: sanity-check prices against the positions' own marks
        marks = {p["symbol"]: float(p.get("current_price") or p.get("avg_entry_price") or 0) for p in broker.positions()}
        closes = {sym: marks.get(sym) or 1.0 for sym in symbols}
    need = [sym for sym in symbols if targets[sym] > 0 or positions.get(sym)]
    stale_ok = dry_run and not clock.get("is_open")
    prices = latest_prices(broker, need, closes, limits, allow_stale=stale_ok) if need else {}
    tol = limits["hold_rebalance_tolerance"] if hold else 0.0
    sizing_equity = equity * (1 - limits["cash_buffer"])
    orders = plan_orders({sym: targets[sym] for sym in need}, positions, prices, sizing_equity,
                         limits["min_order_notional"], tol)
    worst = {sym: p * (1 + limits["price_buffer"]) for sym, p in prices.items()}
    check_orders(orders, worst, equity, {**limits, "max_run_turnover": il["max_run_turnover"]})
    today = now.normalize().tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    done_today = sum(1 for o in broker.closed_orders(today) + broker.open_orders()
                     if str(o.get("client_order_id", "")).startswith(f"tdf-f{fund.number}-"))
    if done_today + len(orders) > il["max_orders_per_day"]:
        raise RiskError(f"{done_today} orders today + {len(orders)} > max {il['max_orders_per_day']} a day")
    buys = sum(o["qty"] * worst[o["symbol"]] for o in orders if o["side"] == "buy")
    sells = sum(o["qty"] * prices[o["symbol"]] * (1 - limits["price_buffer"]) for o in orders if o["side"] == "sell")
    if buys > float(acct["cash"]) + sells:
        raise RiskError(f"buys ${buys:,.0f} exceed cash ${float(acct['cash']):,.0f} plus sells ${sells:,.0f}")
    record.update({"targets": {k: v for k, v in targets.items() if v}, "prices": prices, "orders": orders})

    if dry_run:
        record["status"] = "dry run: no orders submitted"
        return
    tag = (signal or now.floor(f"{minutes}min")).strftime("%Y%m%d%H%M")
    for i, o in enumerate(orders):
        if o["side"] == "buy" and i and orders[i - 1]["side"] == "sell":
            wait_for_fills(broker)        # sells first, so their cash is there for the buys
        coid = f"tdf-f{fund.number}-{tag}-{o['symbol']}-{o['side']}"
        record["pending"] = {"client_order_id": coid, **o}            # outcome unknown if the call raises
        resp = broker.submit_order(o["symbol"], o["qty"], o["side"], coid)
        record["submitted"].append({"client_order_id": coid, "id": resp.get("id"), **o})
        record.pop("pending")
    record["status"] = f"submitted {len(orders)} orders"


def wait_for_fills(broker, timeout_s: float = 20.0) -> None:
    end = time.monotonic() + timeout_s
    while broker.open_orders():
        if time.monotonic() > end:
            raise RiskError(f"sell orders still open after {timeout_s:.0f}s; not buying")
        time.sleep(1)


def run_fund(fund, creds, dry_run: bool, out: Path, shared: dict, now=None) -> int:
    record = {"started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "fund": fund.number,
              "fund_name": fund.label, "kind": "intraday", "dry_run": dry_run, "status": "started",
              "orders": [], "submitted": []}
    code = 0
    try:
        run(dry_run, record, fund, creds, shared, now)
    except Exception as e:  # anything unexpected also means: stop this fund for this bar, no further orders
        n = len(record["submitted"])
        prefix = "NO ORDERS" if n == 0 and "pending" not in record else f"STOPPED AFTER {n} ORDER(S)"
        record["status"] = f"{prefix}: {type(e).__name__}: {e}"
        code = 2
    # quiet bars (nothing to do) are not recorded after the fund's first bar of the run, to keep the ledger readable
    recorded = shared.setdefault("recorded", set())
    if code or record["orders"] or fund.number not in recorded:
        recorded.add(fund.number)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        (out / f"{stamp}-f{fund.number}.json").write_text(json.dumps(record, indent=2, default=str) + "\n")
    print(json.dumps({k: record.get(k) for k in ("fund", "signal_bar", "status", "orders")}, default=str), flush=True)
    return code


def intraday_funds(only: int | None = None) -> list:
    return [f for f in funds.load() if not f.benchmark and funds.timeframe_of(f) != "1Day"
            and (only is None or f.number == only)]


def next_decision(now: pd.Timestamp, minutes: int, delay_s: int) -> pd.Timestamp:
    t = now.floor(f"{minutes}min") + pd.Timedelta(seconds=delay_s)
    return t if t > now else t + pd.Timedelta(minutes=minutes)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--once", action="store_true", help="one decision now instead of looping through the session")
    ap.add_argument("--fund", type=int)
    ap.add_argument("--max-minutes", type=float, default=340, help="stop looping after this long (Actions job limit)")
    ap.add_argument("--out", default=str(ROOT / "experiments" / "executions"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    try:
        keyed = [(f, funds.credentials(f.number)) for f in intraday_funds(a.fund)]
    except Exception as e:
        print(f"NO ORDERS: {type(e).__name__}: {e}")
        return 2
    keyed = [(f, c) for f, c in keyed if c]
    if not keyed:
        print("no intraday fund has paper keys; nothing to do")
        return 0
    il = config.risk_limits()["intraday"]
    minutes = min(bar_minutes(funds.timeframe_of(f)) for f, _ in keyed)
    shared: dict = {}
    if a.once:
        return max(run_fund(f, c, a.dry_run, out, shared) for f, c in keyed)

    clock_broker = PaperBroker(*keyed[0][1])
    deadline = time.monotonic() + a.max_minutes * 60
    worst = 0
    while time.monotonic() < deadline:
        clock = clock_broker.clock()
        now = pd.Timestamp.now(tz=NY)
        if not clock.get("is_open"):
            opens = pd.Timestamp(clock["next_open"]).tz_convert(NY)
            wait = (opens - now).total_seconds()
            if shared.get("traded") or wait > (deadline - time.monotonic()):
                break             # the session is over, or the next one starts after this job ends
            time.sleep(min(max(wait, 1), 600))
            continue
        nxt = next_decision(now, minutes, int(il["decision_delay_seconds"]))
        time.sleep(max((nxt - pd.Timestamp.now(tz=NY)).total_seconds(), 0))
        if time.monotonic() >= deadline:
            break
        shared["traded"] = True
        tick = pd.Timestamp.now(tz=NY)
        failed = [(f, c) for f, c in keyed if run_fund(f, c, a.dry_run, out, shared, tick)]
        worst = max([worst] + [2 for _ in failed])
        # a fund that failed in the closing window retries every minute, so nothing is left open overnight
        close_at = pd.Timestamp(clock["next_close"]).tz_convert(NY)
        flat_from = close_at - pd.Timedelta(minutes=minutes * int(il["flatten_bars_before_close"]))
        while failed and flat_from <= pd.Timestamp.now(tz=NY) < close_at - pd.Timedelta(minutes=2):
            time.sleep(60)
            tick = pd.Timestamp.now(tz=NY)
            failed = [(f, c) for f, c in failed if run_fund(f, c, a.dry_run, out, shared, tick)]
    return worst


if __name__ == "__main__":
    sys.exit(main())
