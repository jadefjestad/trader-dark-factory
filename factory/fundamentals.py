"""Point-in-time fundamentals from SEC EDGAR companyfacts (issue #30).

Panels (one column per symbol, row t = what was public by bar t's close):
- `gross_profitability`: trailing-four-quarter gross profit / latest total assets (Novy-Marx quality).
- `eps_ttm`: trailing-four-quarter diluted EPS (divide by price for an earnings yield).
- `eps_sue`: latest quarter's diluted EPS minus the same quarter a year earlier, divided by the
  standard deviation of that change over the last eight quarters (standardized unexpected earnings
  with a seasonal random-walk expectation, since analyst estimates are paid data).

Look-ahead rules:
- A value is usable from the bar its filing became public (factory.edgar.available_bar), never from
  the period end.
- Each period keeps its first-filed value: restatements and later comparatives are ignored, so a
  backtest never sees numbers that were corrected after the fact.
- Fourth quarters are derived as the fiscal year minus the three reported quarters, available when
  the annual report is.
- A value goes stale (NaN) when the latest known quarter ended more than 200 days before the bar.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factory import edgar
from factory.data import DataError

TAGS = {   # metric -> us-gaap tags in priority order
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet"],
    "cogs": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
             "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"],
    "gross_profit": ["GrossProfit"],
    "assets": ["Assets"],
    "eps": ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted"],
}
UNITS = {"eps": "USD/shares"}
INSTANT = {"assets"}
QUARTER_DAYS = (70, 120)     # 12- to 16-week quarters (Costco's fourth quarter is 16 weeks)
ANNUAL_DAYS = (340, 390)
STALE_DAYS = 200
COLUMNS = ["symbol", "metric", "start", "end", "val", "accn", "filed"]
PANEL_NAMES = ("gross_profitability", "eps_ttm", "eps_sue")


# ---------------------------------------------------------------- companyfacts -> quarterly table

def extract(facts: dict) -> pd.DataFrame:
    """Raw facts per metric: the highest-priority tag reporting each period, first-filed value."""
    gaap = (facts or {}).get("facts", {}).get("us-gaap", {})
    out = []
    for metric, tags in TAGS.items():
        rows = []
        for rank, tag in enumerate(tags):
            for r in gaap.get(tag, {}).get("units", {}).get(UNITS.get(metric, "USD"), []):
                if r.get("val") is None or not r.get("filed") or not r.get("end"):
                    continue
                rows.append((rank, r.get("start"), r["end"], float(r["val"]), r.get("accn", ""), r["filed"]))
        if not rows:
            continue
        df = pd.DataFrame(rows, columns=["rank", "start", "end", "val", "accn", "filed"])
        df["start"] = df["start"].fillna("")
        df = df.sort_values(["start", "end", "rank", "filed"]).drop_duplicates(["start", "end"], keep="first")
        out.append(df.drop(columns="rank").assign(metric=metric))
    if not out:
        return pd.DataFrame(columns=COLUMNS[1:])
    return pd.concat(out, ignore_index=True)[COLUMNS[1:]]


def quarterize(raw: pd.DataFrame) -> pd.DataFrame:
    """Quarterly flow values (reported three-month periods plus derived fourth quarters) and instants."""
    if raw.empty:
        return raw
    out = [raw[raw["metric"].isin(INSTANT)].assign(start="")]
    flows = raw[~raw["metric"].isin(INSTANT) & (raw["start"] != "")].copy()
    flows["days"] = (pd.to_datetime(flows["end"]) - pd.to_datetime(flows["start"])).dt.days
    for metric, g in flows.groupby("metric"):
        q = g[g["days"].between(*QUARTER_DAYS)]
        derived = []
        qs, qe = pd.to_datetime(q["start"]), pd.to_datetime(q["end"])
        for _, a in g[g["days"].between(*ANNUAL_DAYS)].iterrows():
            a_start, a_end = pd.Timestamp(a["start"]), pd.Timestamp(a["end"])
            if (abs(qe - a_end) <= pd.Timedelta(days=5)).any():
                continue                      # the fourth quarter itself was reported
            inside = q[(qs >= a_start - pd.Timedelta(days=5)) & (qe <= a_end - pd.Timedelta(days=40))]
            if len(inside) != 3:
                continue
            last = inside.loc[inside["filed"].idxmax()]
            later = a if a["filed"] >= last["filed"] else last
            derived.append({"metric": metric, "start": (pd.to_datetime(inside["end"]).max() + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                            "end": a["end"], "val": a["val"] - inside["val"].sum(),
                            "accn": later["accn"], "filed": later["filed"]})
        out.append(q.drop(columns="days"))
        if derived:
            out.append(pd.DataFrame(derived))
    df = pd.concat(out, ignore_index=True)
    # gross profit where it is not tagged: revenue minus cost of revenue for the same quarter
    gp = df[df["metric"] == "gross_profit"]
    rev, cogs = df[df["metric"] == "revenue"], df[df["metric"] == "cogs"]
    m = rev.merge(cogs, on=["start", "end"], suffixes=("", "_c"))
    m = m[~m["end"].isin(gp["end"])]
    if len(m):
        later = m["filed_c"] > m["filed"]
        built = pd.DataFrame({"metric": "gross_profit", "start": m["start"], "end": m["end"],
                              "val": m["val"] - m["val_c"], "accn": m["accn"].where(~later, m["accn_c"]),
                              "filed": m["filed"].where(~later, m["filed_c"])})
        df = pd.concat([df, built], ignore_index=True)
    return df[COLUMNS[1:]].reset_index(drop=True)


def fetch(symbols: list[str], use_cache: bool = True) -> pd.DataFrame:
    """Quarterly fundamentals for the universe (cached per UTC day)."""
    def build():
        frames = []
        for s, ciks in edgar.ciks_for(symbols, use_cache).items():
            # a predecessor registrant's periods fill in history; the first-filed value of a period wins
            q = pd.concat([quarterize(extract(edgar.get_json(edgar.FACTS_URL.format(cik=c)))) for c in ciks],
                          ignore_index=True)
            q = q.sort_values("filed").drop_duplicates(["metric", "start", "end"], keep="first")
            frames.append(q.assign(symbol=s))
        df = pd.concat(frames, ignore_index=True)
        if df.empty:
            raise DataError("SEC companyfacts returned no usable facts")
        return df[COLUMNS]

    return edgar.cached_table("fundamentals", build, use_cache)


# ---------------------------------------------------------------- quarterly table -> panels

def with_bars(table: pd.DataFrame, filings: pd.DataFrame, index: pd.DatetimeIndex) -> pd.DataFrame:
    """Attach each value's first usable bar from its filing's acceptance time."""
    acc = filings.drop_duplicates("accessionNumber").set_index("accessionNumber")["acceptanceDateTime"]
    t = edgar.acceptance_times(table["accn"].map(acc))
    return table.assign(bar=edgar.available_bar(t, table["filed"], index), end=pd.to_datetime(table["end"]))


def _ttm(known: pd.DataFrame) -> float:
    k = known.sort_values("end").tail(4)
    if len(k) < 4:
        return np.nan
    span = (k["end"].iloc[-1] - k["end"].iloc[0]).days
    return float(k["val"].sum()) if 230 <= span <= 310 else np.nan


def _sue(known: pd.DataFrame) -> float:
    k = known.sort_values("end").set_index("end")["val"]
    ends = k.index
    diffs = []
    for e in ends:
        prior = ends[(ends >= e - pd.Timedelta(days=385)) & (ends <= e - pd.Timedelta(days=345))]
        diffs.append(k[e] - k[prior[-1]] if len(prior) else np.nan)
    d = pd.Series(diffs, index=ends).dropna().tail(8)
    if len(d) < 4 or d.index[-1] != ends[-1]:
        return np.nan
    sd = float(d.std(ddof=1))
    return float(d.iloc[-1] / sd) if sd > 0 else np.nan


def _series(rows: pd.DataFrame, index: pd.DatetimeIndex, fn) -> pd.Series:
    """fn(known rows) evaluated whenever new rows become public, carried forward between filings."""
    out = pd.Series(np.nan, index=index)
    rows = rows.dropna(subset=["bar"])
    for b in sorted(rows["bar"].unique()):
        known = rows[rows["bar"] <= b].sort_values("filed").drop_duplicates("end", keep="first")
        out[pd.Timestamp(b)] = fn(known)
    return out.ffill()


def _fresh(rows: pd.DataFrame, index: pd.DatetimeIndex) -> np.ndarray:
    """True where the latest quarter known at the bar ended at most STALE_DAYS earlier."""
    latest = pd.to_datetime(_series(rows, index, lambda k: float(k["end"].max().value)))
    return ((pd.Series(index, index=index) - latest).dt.days <= STALE_DAYS).to_numpy()


def panels(table: pd.DataFrame, filings: pd.DataFrame, index: pd.DatetimeIndex, symbols: list[str]) -> dict:
    """All fundamentals panels at once."""
    idx = pd.DatetimeIndex(index)
    t = with_bars(table, filings, idx)
    res = {n: pd.DataFrame(np.nan, index=index, columns=symbols) for n in PANEL_NAMES}
    for s in symbols:
        d = t[t["symbol"] == s]
        eps, gp, assets = (d[d["metric"] == m] for m in ("eps", "gross_profit", "assets"))
        if len(eps):
            fresh = _fresh(eps, idx)
            res["eps_ttm"][s] = _series(eps, idx, _ttm).where(fresh).to_numpy()
            res["eps_sue"][s] = _series(eps, idx, _sue).where(fresh).to_numpy()
        if len(gp) and len(assets):
            fresh = _fresh(gp, idx)
            a = _series(assets, idx, lambda k: float(k.sort_values("end")["val"].iloc[-1]))
            ratio = _series(gp, idx, _ttm) / a.where(a > 0)
            res["gross_profitability"][s] = ratio.where(fresh).to_numpy()
    return res


# ---------------------------------------------------------------- synthetic data for tests

def synthetic_facts(symbol_seed: int, first_year: int = 2012, last_year: int = 2026) -> dict:
    """A companyfacts-shaped dict with 10-Q quarters, 10-K years (no Q4 row) and a restatement."""
    rng = np.random.default_rng(symbol_seed)
    eps_rows, rev_rows, cogs_rows, assets_rows = [], [], [], []
    base = rng.uniform(1, 3)
    for y in range(first_year, last_year):
        q_eps = []
        for qi, (sm, em) in enumerate(((1, 3), (4, 6), (7, 9), (10, 12))):
            start, end = pd.Timestamp(y, sm, 1), pd.Timestamp(y, em, 1) + pd.offsets.MonthEnd(0)
            e = round(base * (1 + 0.02 * (y - first_year)) + rng.normal(0, 0.15), 2)
            rev = 1e9 * (5 + y - first_year + rng.normal(0, 0.3))
            q_eps.append(e)
            filed = (end + pd.Timedelta(days=int(rng.integers(25, 45)))).strftime("%Y-%m-%d")
            accn = f"{symbol_seed:04d}-{y % 100:02d}-{qi:06d}"
            if qi < 3:   # quarters 1-3 from 10-Qs
                for rows, val in ((eps_rows, e), (rev_rows, rev), (cogs_rows, rev * 0.6)):
                    rows.append({"start": f"{start:%Y-%m-%d}", "end": f"{end:%Y-%m-%d}", "val": val, "accn": accn,
                                 "filed": filed, "form": "10-Q"})
            assets_rows.append({"end": f"{end:%Y-%m-%d}", "val": 4e10 + 1e9 * (y - first_year), "accn": accn,
                                "filed": filed, "form": "10-Q"})
        # 10-K: full year only; fourth quarter must be derived
        fy_end = pd.Timestamp(y, 12, 31)
        filed = (fy_end + pd.Timedelta(days=int(rng.integers(45, 60)))).strftime("%Y-%m-%d")
        accn = f"{symbol_seed:04d}-{y % 100:02d}-{9:06d}"
        eps_rows.append({"start": f"{y}-01-01", "end": f"{y}-12-31", "val": round(sum(q_eps), 2), "accn": accn,
                         "filed": filed, "form": "10-K"})
        yr_rev = sum(r["val"] for r in rev_rows[-3:]) * 4 / 3
        rev_rows.append({"start": f"{y}-01-01", "end": f"{y}-12-31", "val": yr_rev, "accn": accn, "filed": filed, "form": "10-K"})
        cogs_rows.append({"start": f"{y}-01-01", "end": f"{y}-12-31", "val": yr_rev * 0.6, "accn": accn, "filed": filed, "form": "10-K"})
    # a later restatement of the first quarter must never replace the first-filed value
    r0 = dict(eps_rows[0], val=eps_rows[0]["val"] + 100.0, filed=f"{first_year + 2}-03-01", accn="restated")
    eps_rows.append(r0)
    unit = lambda rows, u="USD": {"units": {u: rows}}
    return {"facts": {"us-gaap": {"EarningsPerShareDiluted": unit(eps_rows, "USD/shares"),
                                  "Revenues": unit(rev_rows), "CostOfRevenue": unit(cogs_rows),
                                  "Assets": unit(assets_rows)}}}


def synthetic_table(symbols: list[str]) -> pd.DataFrame:
    frames = [quarterize(extract(synthetic_facts(i + 1))).assign(symbol=s) for i, s in enumerate(symbols)]
    return pd.concat(frames, ignore_index=True)[COLUMNS]


def synthetic_filings(table: pd.DataFrame) -> pd.DataFrame:
    """Acceptance times for the synthetic accessions: some before the close, some after."""
    acc = table.drop_duplicates("accn")[["accn", "filed"]]
    hours = np.where(np.arange(len(acc)) % 2 == 0, "12:30:00", "21:45:00")
    return pd.DataFrame({"accessionNumber": acc["accn"].to_numpy(),
                         "acceptanceDateTime": [f"{f}T{h}.000Z" for f, h in zip(acc["filed"], hours)]})
