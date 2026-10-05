"""The paper funds: up to nine Alpaca paper accounts, each running its own strategy.

state/funds.yaml numbers the funds 1-10 and gives each a display name and emoji (pure decoration, with no
link to strategy) and the strategy it runs now. Agents may move strategies between funds at any time by
a PR to that file. `strategy: champion` follows state/champion.json; anything else is the `strategy`
block of a ledger evaluation record (name, ref, params, timeframe, code_sha256), copied as is.

Credentials come from GitHub secrets ALPACA_FUND_<N>_KEY_ID / ALPACA_FUND_<N>_SECRET_KEY. Fund 1 is the
original paper account and falls back to ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY. A fund without both
keys is skipped.

A fund with a `benchmark` block instead of a strategy (fund 10, Spyder-man) has no account and never
trades: the leaderboard values it as `capital` dollars put into the benchmark symbol at the close of
`start` and held, from dividend-adjusted daily closes, so the funds are compared with plain index holding.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import yaml

from factory import config
from factory.config import ROOT

FUNDS = ROOT / "state" / "funds.yaml"
CHAMPION = ROOT / "state" / "champion.json"
MAX_FUNDS = 10


class FundError(RuntimeError):
    pass


@dataclass(frozen=True)
class Fund:
    number: int
    name: str
    emoji: str
    strategy: object   # "champion" or a ledger strategy dict; None for a benchmark fund
    benchmark: dict | None = None   # {"symbol", "start", "capital"} for a tracked, untraded benchmark

    @property
    def label(self) -> str:
        return f"{self.emoji} {self.name}"


def load(path=None) -> list[Fund]:
    raw = yaml.safe_load((path or FUNDS).read_text()) or {}
    funds = []
    for n, f in sorted((raw.get("funds") or {}).items()):
        if not isinstance(n, int) or not 1 <= n <= MAX_FUNDS:
            raise FundError(f"fund number {n!r} must be an integer from 1 to {MAX_FUNDS}")
        if not f.get("name") or not f.get("emoji"):
            raise FundError(f"fund {n} needs a name and an emoji")
        if b := f.get("benchmark"):
            if f.get("strategy") or not (b.get("symbol") and b.get("start") and float(b.get("capital", 0)) > 0):
                raise FundError(f"fund {n}: a benchmark fund needs symbol, start and capital, and no strategy")
            funds.append(Fund(n, str(f["name"]), str(f["emoji"]), None,
                              {"symbol": str(b["symbol"]), "start": str(b["start"]), "capital": float(b["capital"])}))
            continue
        s = f.get("strategy")
        if s != "champion" and not (isinstance(s, dict) and s.get("ref") and s.get("name")):
            raise FundError(f"fund {n}: strategy must be 'champion' or a ledger strategy block with name and ref")
        funds.append(Fund(n, str(f["name"]), str(f["emoji"]), s))
    return funds


def credentials(number: int, env=None) -> tuple[str, str] | None:
    env = os.environ if env is None else env
    key, secret = env.get(f"ALPACA_FUND_{number}_KEY_ID"), env.get(f"ALPACA_FUND_{number}_SECRET_KEY")
    if number == 1 and not (key and secret):
        key, secret = env.get("ALPACA_API_KEY_ID"), env.get("ALPACA_API_SECRET_KEY")
    return (key, secret) if key and secret else None


def strategy(fund: Fund, champion_path=None) -> dict:
    """The strategy record the fund runs, with the candidate file checked against its recorded hash."""
    if fund.benchmark:
        raise FundError(f"fund {fund.number} is a benchmark and runs no strategy")
    if fund.strategy == "champion":
        s = dict(json.loads((champion_path or CHAMPION).read_text()))
        s["champion"] = True
    else:
        s = dict(fund.strategy)
    if s["ref"].endswith(".py"):
        path = ROOT / s["ref"]
        if not path.is_file() or config.file_sha256(path) != s.get("code_sha256"):
            raise FundError(f"fund {fund.number}: code missing or hash mismatch for {s['ref']}")
    return s
