"""Pre-trade risk checks. Every function raises RiskError instead of adjusting silently."""
from __future__ import annotations

import math

from factory.invariants import require_paper


class RiskError(RuntimeError):
    pass


def check_account(acct: dict, limits: dict) -> None:
    try:
        require_paper(limits, acct.get("account_number", ""))
    except RuntimeError as e:
        raise RiskError(str(e)) from None
    if acct.get("status") != "ACTIVE":
        raise RiskError(f"account status {acct.get('status')}")
    if acct.get("trading_blocked") or acct.get("account_blocked"):
        raise RiskError("account is blocked")


def check_drawdown(equity: float, history_equity: list, limits: dict) -> float:
    vals = [float(x) for x in history_equity if x is not None and float(x) > 0]
    peak = max(vals + [equity])
    dd = 1 - equity / peak if peak > 0 else 0.0
    if dd > limits["max_drawdown_halt"]:
        raise RiskError(f"drawdown {dd:.1%} exceeds halt level {limits['max_drawdown_halt']:.0%}")
    return dd


def check_targets(targets: dict, universe: list, limits: dict) -> None:
    for sym, w in targets.items():
        if sym not in universe:
            raise RiskError(f"{sym} is not in the protected universe")
        if not math.isfinite(w):
            raise RiskError(f"non-finite weight for {sym}")
        if w < -1e-9 and not limits["allow_short"]:
            raise RiskError(f"short weight for {sym} while shorting is disabled")
        if abs(w) > limits["max_position_weight"] + 1e-9:
            raise RiskError(f"{sym} weight {w:.3f} > {limits['max_position_weight']}")
    gross = sum(abs(w) for w in targets.values())
    if gross > limits["max_gross_exposure"] + 1e-9:
        raise RiskError(f"gross exposure {gross:.3f} > {limits['max_gross_exposure']}")


def check_orders(orders: list, prices: dict, equity: float, limits: dict) -> None:
    if len(orders) > limits["max_orders_per_run"]:
        raise RiskError(f"{len(orders)} orders > max {limits['max_orders_per_run']}")
    total = 0.0
    for o in orders:
        px = prices[o["symbol"]]
        if px < limits["min_price"]:
            raise RiskError(f"{o['symbol']} price {px} below min {limits['min_price']}")
        notional = o["qty"] * px
        if notional > limits["max_order_notional"]:
            raise RiskError(f"{o['symbol']} order ${notional:,.0f} > max ${limits['max_order_notional']:,}")
        total += notional
    if equity > 0 and total / equity > limits["max_run_turnover"] + 1e-9:
        raise RiskError(f"run turnover {total / equity:.2f} > max {limits['max_run_turnover']}")
