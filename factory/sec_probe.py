"""Coverage and sanity report for the SEC panels on real data (run in Actions, which has the network).

    python -m factory.sec_probe [--out sec_probe.json]

Reports filing counts, the acceptance-time convention, panel coverage, and each panel's monthly rank
correlation with the next month's return over in-sample plus validation only (the holdout is never
looked at here).
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import numpy as np
import pandas as pd

from factory import config, edgar, extras
from factory.evaluate import load_data

SEC_PANELS = ["gross_profitability", "eps_ttm", "eps_sue", "insider_buyers", "insider_buy_value",
              "earnings_reaction", "earnings_age"]
RESEARCH_END = "2023-12-31"   # end of validation: the holdout stays unseen


def rank_ic(panel: pd.DataFrame, close: pd.DataFrame, horizon: int = 21) -> dict:
    fwd = close.shift(-horizon) / close - 1
    month_end = close.index.to_series().groupby(close.index.to_period("M")).last()
    ics = []
    for d in month_end:
        if d > pd.Timestamp(RESEARCH_END) - pd.Timedelta(days=35):
            continue
        x, y = panel.loc[d], fwd.loc[d]
        ok = x.notna() & y.notna()
        if ok.sum() >= 8 and x[ok].nunique() > 2:
            ics.append(x[ok].rank().corr(y[ok].rank()))
    ics = pd.Series(ics, dtype=float)
    return {"months": int(len(ics)), "mean_ic": round(float(ics.mean()), 4) if len(ics) else None,
            "t": round(float(ics.mean() / ics.std() * np.sqrt(len(ics))), 2) if len(ics) > 2 and ics.std() > 0 else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res: dict = {}
    t0 = time.time()
    symbols = config.universe()["symbols"]
    try:
        res["ciks"] = edgar.cik_map(symbols)
        fil = edgar.filings(symbols)
        res["filings_seconds"] = round(time.time() - t0)
        res["filings_by_form"] = fil.groupby("form").size().to_dict()
        res["filings_first"] = fil.groupby("symbol")["filingDate"].min().to_dict()
        ek = fil[(fil["form"] == "8-K") & fil["items"].fillna("").astype(str).str.contains("2.02", regex=False)]
        res["earnings_8k_per_symbol"] = ek.groupby("symbol").size().to_dict()
        res["aapl_2_02_acceptance"] = ek[ek["symbol"] == "AAPL"].sort_values("filingDate").tail(6)[
            ["filingDate", "acceptanceDateTime"]].values.tolist()
        res["acceptance_hour_hist"] = edgar.acceptance_times(ek["acceptanceDateTime"]).dt.hour.value_counts().sort_index().to_dict()
    except Exception as e:
        res["filings_error"] = f"{type(e).__name__}: {e}"[:300]
    try:
        from factory import fundamentals
        t1 = time.time()
        tab = fundamentals.fetch(symbols)
        res["fundamentals_seconds"] = round(time.time() - t1)
        res["fundamentals_rows"] = tab.groupby(["metric"]).size().to_dict()
        res["fundamentals_missing"] = {m: sorted(set(symbols) - set(tab[tab["metric"] == m]["symbol"]))
                                       for m in ("eps", "gross_profit", "assets")}
        acc = set(fil["accessionNumber"])
        res["fundamentals_accn_with_acceptance"] = round(float(tab["accn"].isin(acc).mean()), 3)
    except Exception as e:
        res["fundamentals_error"] = f"{type(e).__name__}: {e}"[:300]
    try:
        from factory import insiders
        t1 = time.time()
        ins = insiders.fetch(symbols, fil)
        res["insiders_seconds"] = round(time.time() - t1)
        res["insider_buys_per_symbol"] = ins.groupby("symbol").size().to_dict()
        res["insider_buys_per_year"] = ins.groupby(ins["filed"].astype(str).str[:4]).size().to_dict()
        res["insider_accn_with_acceptance"] = round(float(ins["accn"].isin(set(fil["accessionNumber"])).mean()), 3) if len(ins) else None
    except Exception as e:
        res["insiders_error"] = f"{type(e).__name__}: {e}"[:300]
    try:
        md, _ = load_data("1Day", "alpaca", config.evaluation())
        md = extras.attach(md, SEC_PANELS, "alpaca")
        close = md.close.loc[:RESEARCH_END]
        cov, ic = {}, {}
        for n in SEC_PANELS:
            p = md.extra[n].loc["2017-01-01":RESEARCH_END]
            cov[n] = {"notna": round(float(p.notna().mean().mean()), 3),
                      "symbols_never": [s for s in p.columns if p[s].isna().all()]}
            ic[n] = rank_ic(md.extra[n].loc[:RESEARCH_END], close)
        res["panel_coverage_2017_2023"] = cov
        res["panel_rank_ic_21d_2015_2023"] = ic
        res["latest_bar"] = str(md.index[-1].date())
        res["latest_row"] = {n: md.extra[n].iloc[-1].round(3).dropna().to_dict() for n in ("eps_sue", "insider_buyers", "earnings_age")}
    except Exception as e:
        res["panels_error"] = f"{type(e).__name__}: {e}"[:300]
    res["seconds"] = round(time.time() - t0)
    text = json.dumps(res, indent=1, default=str)
    print(text)
    if a.out:
        open(a.out, "w").write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
