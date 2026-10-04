"""Evaluate a strategy against protected rules, baselines, a benchmark and the current champion.

    python -m factory.evaluate --candidate strategies/candidates/my_idea.py --data alpaca
    python -m factory.evaluate --baselines --data synthetic

Writes <out>/<experiment_id>.json and .md. With --write-promotion, a candidate that passes every
gate and beats the champion is written to state/champion.json (merging that PR = promotion).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from factory import backtest, config, extras, metrics, runner
from factory.config import ROOT
from factory.data import DataError, MarketData, load_alpaca, synthetic, validate

CHAMPION = ROOT / "state" / "champion.json"


# ---------------------------------------------------------------- data

def load_data(timeframe: str, source: str, cfg: dict) -> tuple[MarketData, MarketData]:
    """Return (universe data, benchmark data) covering warmup through the end of the holdout."""
    uni = config.universe()
    symbols, bench = uni["symbols"], uni["benchmark"]
    per = cfg["periods"][timeframe]
    start = (pd.Timestamp(per["in_sample"]["start"]) - pd.Timedelta(days=int(per["warmup_days"] * 1.5))).strftime("%Y-%m-%d")
    end = per["holdout"]["end"]
    if source == "synthetic":
        md = synthetic(symbols + [bench], start=start, end="2026-06-30" if end == "latest" else end, timeframe=timeframe)
    else:
        d = cfg["data"]
        md = load_alpaca(symbols + [bench], start, end, timeframe, feed=d["historical_feed"],
                         fallback_feed=d.get("fallback_feed"), adjustment=d["adjustment"])
    validate(md, symbols + [bench])
    return md.select(symbols), md.select([bench])


def periods(timeframe: str, cfg: dict, index: pd.Index) -> dict:
    out = {}
    for name in ("in_sample", "validation", "holdout"):
        p = cfg["periods"][timeframe][name]
        end = index[-1] if p["end"] == "latest" else pd.Timestamp(p["end"]) + pd.Timedelta(hours=23, minutes=59)
        start = pd.Timestamp(p["start"])
        if getattr(index, "tz", None) is not None:
            start = start.tz_localize(index.tz)
            if not isinstance(end, pd.Timestamp) or end.tzinfo is None:
                end = pd.Timestamp(end).tz_localize(index.tz)
        out[name] = (start, end)
    return out


# ---------------------------------------------------------------- checks

def weight_violations(w: pd.DataFrame, limits: dict) -> list[str]:
    v = []
    if not np.isfinite(w.fillna(0).values).all():
        v.append("non-finite weights")
    if not limits["allow_short"] and (w < -1e-9).any().any():
        v.append("negative weights while shorting is disabled")
    gross = w.abs().sum(axis=1).max()
    if gross > limits["max_gross_exposure"] + 1e-6:
        v.append(f"gross exposure {gross:.3f} > {limits['max_gross_exposure']}")
    biggest = w.abs().max().max()
    if biggest > limits["max_position_weight"] + 1e-6:
        v.append(f"position weight {biggest:.3f} > {limits['max_position_weight']}")
    return v


def cut_points(n_bars: int, lookback: int, n: int, seed: int = 0) -> list[int]:
    rng = np.random.default_rng(seed)
    lo = min(max(lookback + 5, n_bars // 4), n_bars - 2)
    return sorted(set(rng.integers(lo, n_bars - 1, n).tolist()))


def causality_mismatches(full: pd.DataFrame, truncated: dict[int, pd.DataFrame]) -> list[str]:
    """The last row of each truncated rerun must equal the full run's row at that bar (NaN == NaN)."""
    bad = []
    for cut, part in truncated.items():
        if not np.allclose(part.iloc[-1].values, full.iloc[cut].values, atol=1e-9, equal_nan=True):
            bad.append(str(full.index[cut]))
    return bad


def perturbations(params: dict, frac: float) -> list[dict]:
    out = []
    for k, v in params.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        for s in (1 - frac, 1 + frac):
            nv = type(v)(round(v * s)) if isinstance(v, int) else v * s
            if nv != v and nv > 0:
                out.append({**params, k: nv})
    return out


# ---------------------------------------------------------------- core

def backtest_weights(w, md, cfg):
    return backtest.run(w, md, cfg["costs"][md.timeframe], cfg["initial_capital"], cfg.get("min_trade_weight", 0.0))


def stressed_costs(costs: dict, multiple: float) -> dict:
    """Every per-trade cost scaled by `multiple` (commission per share included)."""
    return {k: (v * multiple if isinstance(v, (int, float)) else v) for k, v in costs.items()}


def cost_stress_sharpe(w, md, cfg, pers) -> float:
    cs = cfg["gates"]["cost_stress"]
    res = backtest.run(w, md, stressed_costs(cfg["costs"][md.timeframe], cs["multiple"]),
                       cfg["initial_capital"], cfg.get("min_trade_weight", 0.0))
    return metrics.summarize(res, *pers["validation"]).get("sharpe", 0.0)


def period_metrics(res, pers):
    return {name: metrics.summarize(res, a, b) for name, (a, b) in pers.items()}


def score(pm: dict) -> float:
    return (pm["validation"].get("sharpe", 0.0) + pm["holdout"].get("sharpe", 0.0)) / 2


def verify_champion_code(ch: dict, root: Path = ROOT) -> None:
    if ch["ref"].endswith(".py"):
        path = root / ch["ref"]
        if not path.is_file() or config.file_sha256(path) != ch.get("code_sha256"):
            raise DataError(f"champion code {ch['ref']} is missing or does not match its recorded hash")


def evaluate(ref: str, source: str = "synthetic", experiment_id: str | None = None,
             include_baselines: bool = True) -> dict:
    """Score one strategy. All strategy code runs in factory.runner's child process."""
    cfg = config.evaluation()
    limits = config.risk_limits()
    gates = cfg["gates"]
    meta = runner.describe(ref)
    tf = meta["timeframe"]
    md, bench = load_data(tf, source, cfg)
    md = extras.attach(md, meta.get("extra_data"), source)
    if CHAMPION.exists():   # the champion is re-scored on the same data, so give it its panels too
        ch_ref = json.loads(CHAMPION.read_text()).get("ref")
        if ch_ref and ch_ref != ref:
            need = [x for x in runner.describe(ch_ref).get("extra_data", []) if x not in md.extra]
            md = extras.attach(md, need, source)
    pers = periods(tf, cfg, md.index)

    cuts = cut_points(len(md.index), meta["lookback"], gates["causality_checks"])
    perturbed = perturbations(meta["params"], gates["robustness_perturbation"])
    live_bars = int(meta["lookback"])           # the least history factory.execute will hand the strategy
    jobs = ([{"params": None, "rows": None}] + [{"params": None, "rows": c + 1} for c in cuts]
            + [{"params": p, "rows": None} for p in perturbed]
            + [{"params": None, "rows": c + 1, "start": max(0, c + 1 - live_bars)} for c in cuts])
    frames = runner.run(ref, md, jobs)
    window_frames = frames[len(frames) - len(cuts):]
    frames = frames[:len(frames) - len(cuts)]
    w = frames[0]
    res = backtest_weights(w, md, cfg)
    pm = period_metrics(res, pers)
    violations = weight_violations(w, limits)
    leaks = causality_mismatches(w, dict(zip(cuts, frames[1:1 + len(cuts)])))
    short = causality_mismatches(w, dict(zip(cuts, window_frames)))

    base_sharpe = pm["validation"].get("sharpe", 0.0)
    robust = [metrics.summarize(backtest_weights(f, md, cfg), *pers["validation"]).get("sharpe", 0.0)
              for f in frames[1 + len(cuts):]]
    robust_ratio = float(np.median(robust) / base_sharpe) if robust and base_sharpe > 0 else (1.0 if not robust else 0.0)

    # benchmark: buy and hold the benchmark ETF
    bw = pd.DataFrame(1.0, index=bench.index, columns=bench.symbols)
    bench_pm = period_metrics(backtest_weights(bw, bench, cfg), pers)

    baselines = {}
    if include_baselines:
        from strategies import baselines as B
        for bcls in B.ALL:
            bref = f"{bcls.__module__}:{bcls.__name__}"
            if bcls.timeframe == tf and bref != ref:
                baselines[bcls.name] = period_metrics(backtest_weights(runner.run(bref, md, [{}])[0], md, cfg), pers)

    champion = None
    if CHAMPION.exists():
        ch = json.loads(CHAMPION.read_text())
        verify_champion_code(ch)
        if ch.get("timeframe", "1Day") == tf:
            cw = runner.run(ch["ref"], md, [{"params": ch.get("params")}])[0]
            cpm = period_metrics(backtest_weights(cw, md, cfg), pers)
            champion = {"ref": ch["ref"], "name": ch.get("name"), "score": score(cpm), "metrics": cpm}

    g = []
    def gate(name, ok, detail):
        g.append({"gate": name, "passed": bool(ok), "detail": detail})
    gate("data_not_synthetic", source != "synthetic" or cfg["promotion"]["synthetic_data_promotable"], md.source)
    gate("executable_timeframe", tf in cfg["promotion"]["executable_timeframes"], tf)
    gate("risk_limits", not violations, "; ".join(violations) or "ok")
    gate("no_lookahead", not leaks, f"mismatch at {leaks}" if leaks else f"{len(cuts)} truncated reruns matched")
    gate("lookback_sufficient", not short,
         f"with only {live_bars} bars (as live) signals differ at {short}" if short
         else f"{len(cuts)} {live_bars}-bar reruns matched")
    gate("min_trades_validation", pm["validation"].get("trades", 0) >= gates["min_trades_validation"], pm["validation"].get("trades", 0))
    for name in pers:
        dd, vol = pm[name].get("max_drawdown", 1), pm[name].get("annual_vol", 1)
        hidden = name == "holdout"   # holdout gates report pass/fail only
        gate(f"max_drawdown_{name}", dd <= gates["max_drawdown"], "hidden" if hidden else dd)
        gate(f"max_vol_{name}", vol <= gates["max_annual_vol"], "hidden" if hidden else vol)
    gate("min_validation_sharpe", base_sharpe >= gates["min_validation_sharpe"], base_sharpe)
    gate("min_holdout_sharpe", pm["holdout"].get("sharpe", -9) >= gates["min_holdout_sharpe"], "hidden")
    decay = pm["in_sample"].get("sharpe", 0) - base_sharpe
    gate("sharpe_decay", decay <= gates["max_sharpe_decay"], round(decay, 3))
    gate("turnover", pm["validation"].get("annual_turnover", 1e9) <= gates["max_annual_turnover"], pm["validation"].get("annual_turnover"))
    gate("robustness", robust_ratio >= gates["robustness_min_ratio"], round(robust_ratio, 3))
    gate("fill_participation", res.max_participation <= cfg["max_participation"], round(res.max_participation, 5))
    cs = gates.get("cost_stress")
    if cs and tf in cs["timeframes"]:
        stressed = cost_stress_sharpe(w, md, cfg, pers)
        gate("cost_stress", stressed >= cs["min_validation_sharpe"], f"{cs['multiple']}x costs: validation Sharpe {round(stressed, 3)}")

    passed = all(x["passed"] for x in g)
    # report-only selection-bias check on the validation period (issue #49)
    v0, v1 = pers["validation"]
    dsr = metrics.deflated_sharpe(res.returns.loc[v0:v1], experiment_trials())
    sc = score(pm)
    beats = champion is None or sc >= champion["score"] + cfg["promotion"]["min_score_improvement"]
    exp_id = experiment_id or f"{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S}-{meta['name']}"
    ref_path = ROOT / ref if ref.endswith(".py") else None
    return {
        "experiment_id": exp_id,
        "strategy": {"name": meta["name"], "ref": ref, "params": meta["params"], "timeframe": tf,
                     "code_sha256": config.file_sha256(ref_path) if ref_path and ref_path.exists() else None},
        "data": {"source": md.source, "fingerprint": md.fingerprint(), "first_bar": str(md.index[0]), "last_bar": str(md.index[-1])},
        "protected_fingerprint": config.protected_fingerprint(),
        "evaluated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "metrics": _redact_holdout(pm),
        "benchmark": {"symbol": bench.symbols[0], "metrics": _redact_holdout(bench_pm)},
        "baselines": {k: _redact_holdout(v) for k, v in baselines.items()},
        "champion": None if champion is None else {"ref": champion["ref"], "name": champion["name"],
                                                    "metrics": _redact_holdout(champion["metrics"])},
        "gates": g,
        "deflated_sharpe": dsr,
        "passed_gates": passed,
        "beats_champion": bool(beats),
        "promote": bool(passed and beats),
    }


def experiment_trials() -> int:
    """How many experiments have been tried: FACTORY_TRIALS (set by CI from the PR history), else the
    candidate files on disk plus the baselines."""
    import os
    env = os.environ.get("FACTORY_TRIALS", "")
    if env.isdigit() and int(env) > 0:
        return int(env)
    from strategies import baselines
    return len(list((ROOT / "strategies" / "candidates").glob("*.py"))) + len(baselines.ALL)


def _redact_holdout(pm: dict) -> dict:
    """The holdout stays 'unseen': report only coarse figures so the agent cannot tune to it."""
    out = dict(pm)
    h = pm.get("holdout", {})
    out["holdout"] = {"sharpe": round(h.get("sharpe", 0.0), 1), "max_drawdown": round(h.get("max_drawdown", 0.0), 1)}
    return out


# ---------------------------------------------------------------- reporting

def to_markdown(r: dict) -> str:
    s = r["strategy"]
    verdict = "PROMOTE" if r["promote"] else ("PASSED GATES, did not beat champion" if r["passed_gates"] else "REJECTED")
    lines = [f"## Experiment `{r['experiment_id']}`: **{verdict}**", "",
             f"Strategy `{s['name']}` ({s['timeframe']}), params `{json.dumps(s['params'])}`",
             f"Data `{r['data']['source']}` {r['data']['first_bar'][:10]} to {r['data']['last_bar'][:10]}, "
             f"fingerprint `{r['data']['fingerprint']}`, rules `{r['protected_fingerprint']}`", ""]
    if r["champion"]:
        lines.append(f"Beats champion `{r['champion']['name']}` (validation + holdout Sharpe, margin per rules): "
                     f"**{'yes' if r['beats_champion'] else 'no'}**")
    lines += ["", "| Period | Sharpe | CAGR | Vol | Max DD | Turnover/yr | Trades |", "|---|---|---|---|---|---|---|"]
    for p, m in r["metrics"].items():
        lines.append(f"| {p} | {m.get('sharpe','')} | {m.get('cagr','')} | {m.get('annual_vol','')} | "
                     f"{m.get('max_drawdown','')} | {m.get('annual_turnover','')} | {m.get('trades','')} |")
    lines += ["", f"Validation Sharpe vs others: benchmark {r['benchmark']['symbol']} "
              f"{r['benchmark']['metrics']['validation'].get('sharpe')}"]
    for k, v in r["baselines"].items():
        lines.append(f"- {k}: {v['validation'].get('sharpe')}")
    d = r.get("deflated_sharpe") or {}
    if d.get("probability") is not None:
        lines += ["", f"Selection-bias check (report only): after {d['trials']} experiments, probability the validation "
                      f"Sharpe beats luck is {d['probability']} (luck benchmark {d['benchmark_annual_sharpe']} annual)."]
    lines += ["", "| Gate | Result | Detail |", "|---|---|---|"]
    for x in r["gates"]:
        lines.append(f"| {x['gate']} | {'pass' if x['passed'] else '**FAIL**'} | {x['detail']} |")
    return "\n".join(lines) + "\n"


def write_promotion(r: dict) -> None:
    CHAMPION.parent.mkdir(exist_ok=True)
    CHAMPION.write_text(json.dumps({
        "ref": r["strategy"]["ref"], "params": r["strategy"]["params"], "name": r["strategy"]["name"],
        "timeframe": r["strategy"]["timeframe"], "code_sha256": r["strategy"]["code_sha256"],
        "experiment_id": r["experiment_id"], "promoted_at": r["evaluated_at"],
    }, indent=2) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--candidate", help="strategy file or module:Class")
    g.add_argument("--baselines", action="store_true", help="evaluate every baseline (leaderboard)")
    ap.add_argument("--data", choices=["synthetic", "alpaca"], default="synthetic")
    ap.add_argument("--out", default=str(ROOT / "experiments" / "results"))
    ap.add_argument("--experiment-id")
    ap.add_argument("--write-promotion", action="store_true")
    ap.add_argument("--timeframes", default="1Day", help="with --baselines: which timeframes to include")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if a.candidate:
        refs = [a.candidate]
    else:
        from strategies import baselines
        wanted = set(a.timeframes.split(","))
        refs = [f"{c.__module__}:{c.__name__}" for c in baselines.ALL if c.timeframe in wanted]
    try:
        for ref in refs:
            r = evaluate(ref, a.data, a.experiment_id if a.candidate else None)
            (out / f"{r['experiment_id']}.json").write_text(json.dumps(r, indent=2, default=str) + "\n")
            (out / f"{r['experiment_id']}.md").write_text(to_markdown(r))
            print(to_markdown(r))
            if a.write_promotion and a.candidate and r["promote"]:
                write_promotion(r)
                print(f"champion updated -> {r['strategy']['name']}")
    except (DataError, runner.StrategyError) as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
