"""Insider open-market purchases from SEC Form 4 (issue #64).

Panels (one column per symbol, row t = what was public by bar t's close):
- `insider_buyers`: distinct insiders with an open-market purchase (transaction code P) made public in
  the last 90 calendar days.
- `insider_buy_value`: dollar value of those purchases over the same window.

Sources: SEC's quarterly Insider Transactions Data Sets for complete quarters (cached on disk for
good; past quarters never change), plus the Form 4 XML of filings made after the newest published
quarter, so the panel stays current for live execution. Amendments (4/A) are skipped so a corrected
filing is not counted twice.

Look-ahead rule: a purchase counts from the bar its Form 4 was accepted by EDGAR (factory.edgar),
never from the trade date.
"""
from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from factory import edgar
from factory.data import CACHE_DIR, DataError

DATASET_URL = ("https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/"
               "{y}q{q}_form345.zip")
FIRST_QUARTER = (2014, 1)
WINDOW = pd.Timedelta(days=90)
COLUMNS = ["accn", "issuer_cik", "owner", "filed", "trans_date", "shares", "price"]
PANEL_NAMES = ("insider_buyers", "insider_buy_value")


def _quarters(today: pd.Timestamp):
    y, q = FIRST_QUARTER
    while (y, q) <= (today.year, (today.month - 1) // 3 + 1):
        yield y, q
        y, q = (y + 1, 1) if q == 4 else (y, q + 1)


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def parse_dataset(data: bytes, ciks: set[int]) -> pd.DataFrame:
    """Open-market purchases by insiders of `ciks` from one quarterly data set zip."""
    sub = edgar.read_zip_member(data, "SUBMISSION.tsv")
    sub = sub[(sub["DOCUMENT_TYPE"] == "4") & _num(sub["ISSUERCIK"]).isin(ciks)]
    tr = edgar.read_zip_member(data, "NONDERIV_TRANS.tsv")
    tr = tr[(tr["TRANS_CODE"] == "P") & (tr["TRANS_ACQUIRED_DISP_CD"] == "A")
            & tr["ACCESSION_NUMBER"].isin(sub["ACCESSION_NUMBER"])]
    own = edgar.read_zip_member(data, "REPORTINGOWNER.tsv")
    own = own[own["ACCESSION_NUMBER"].isin(tr["ACCESSION_NUMBER"])]
    owner = own.groupby("ACCESSION_NUMBER")["RPTOWNERCIK"].min()
    s = sub.set_index("ACCESSION_NUMBER")
    out = pd.DataFrame({
        "accn": tr["ACCESSION_NUMBER"].to_numpy(),
        "issuer_cik": _num(tr["ACCESSION_NUMBER"].map(s["ISSUERCIK"])).to_numpy(),
        "owner": tr["ACCESSION_NUMBER"].map(owner).fillna("").astype(str).str.lstrip("0").to_numpy(),
        "filed": pd.to_datetime(tr["ACCESSION_NUMBER"].map(s["FILING_DATE"]), format="mixed", dayfirst=False,
                                errors="coerce").dt.strftime("%Y-%m-%d").to_numpy(),
        "trans_date": pd.to_datetime(tr["TRANS_DATE"], format="mixed", errors="coerce").dt.strftime("%Y-%m-%d").to_numpy(),
        "shares": _num(tr["TRANS_SHARES"]).to_numpy(),
        "price": _num(tr["TRANS_PRICEPERSHARE"]).to_numpy(),
    })
    return out[COLUMNS]


def quarter_purchases(y: int, q: int, ciks: set[int], use_cache: bool = True) -> pd.DataFrame | None:
    """One complete quarter (None if SEC has not published it yet). Cached permanently once read."""
    key = hashlib.sha256(",".join(map(str, sorted(ciks))).encode()).hexdigest()[:8]   # one file per universe
    path = CACHE_DIR / f"sec_insiders_{y}q{q}_{key}.csv.gz"
    if use_cache and path.exists():
        return pd.read_csv(path, dtype={"accn": str, "owner": str}, keep_default_na=False, na_values=[""])
    data = edgar.get(DATASET_URL.format(y=y, q=q), missing_ok=True)
    if data is None:
        return None
    df = parse_dataset(data, ciks)
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    return df


def parse_form4(xml: bytes, accn: str, issuer_cik: int, filed: str) -> list[dict]:
    """Open-market purchases from one Form 4 XML document."""
    root = ET.fromstring(xml)
    val = lambda node, path: (node.findtext(path + "/value") or node.findtext(path) or "").strip()
    owner = (root.findtext("reportingOwner/reportingOwnerId/rptOwnerCik") or "").strip()
    rows = []
    for t in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
        if (t.findtext("transactionCoding/transactionCode") or "").strip() != "P":
            continue
        if val(t, "transactionAmounts/transactionAcquiredDisposedCode") != "A":
            continue
        rows.append({"accn": accn, "issuer_cik": issuer_cik, "owner": owner.lstrip("0"), "filed": filed,
                     "trans_date": val(t, "transactionDate")[:10],
                     "shares": pd.to_numeric(val(t, "transactionAmounts/transactionShares"), errors="coerce"),
                     "price": pd.to_numeric(val(t, "transactionAmounts/transactionPricePerShare"), errors="coerce")})
    return rows


def recent_purchases(filings: pd.DataFrame, after: str, use_cache: bool = True) -> pd.DataFrame:
    """Purchases in Form 4s filed after `after` (not yet in a published data set), from their XML."""
    def build():
        f = filings[(filings["form"] == "4") & (filings["filingDate"] > after)]
        rows = []
        for _, r in f.iterrows():
            doc = str(r["primaryDocument"]).split("/")[-1]      # drop the xslF345X05/ rendering prefix
            acc = str(r["accessionNumber"])
            xml = edgar.get(edgar.ARCHIVE_URL.format(cik=int(r["cik"]), acc=acc.replace("-", ""), doc=doc))
            rows += parse_form4(xml, acc, int(r["cik"]), str(r["filingDate"]))
        return pd.DataFrame(rows, columns=COLUMNS)

    return edgar.cached_table("insiders_recent", build, use_cache)


def fetch(symbols: list[str], filings: pd.DataFrame, use_cache: bool = True) -> pd.DataFrame:
    """Every open-market purchase in the universe since FIRST_QUARTER, with a `symbol` column.

    Cached per UTC day as a whole, so the evaluate job (no network) never asks SEC whether a quarter
    has been published since the data job looked."""
    def build():
        by_cik = {c: s for s, ciks in edgar.ciks_for(symbols, use_cache).items() for c in ciks}
        today = pd.Timestamp.now(tz="UTC").tz_localize(None)
        frames, covered = [], None
        quarters = list(_quarters(today))
        for i, (y, q) in enumerate(quarters):
            df = quarter_purchases(y, q, set(by_cik), use_cache)
            if df is None:
                if i < len(quarters) - 3:    # SEC publishes a quarter some months after it ends
                    raise DataError(f"SEC insider data set {y}q{q} is missing")
                continue
            frames.append(df)
            covered = pd.Timestamp(y, 3 * q, 1) + pd.offsets.MonthEnd(0)
        if covered is None:
            raise DataError("no SEC insider data sets available")
        frames.append(recent_purchases(filings, covered.strftime("%Y-%m-%d"), use_cache))
        out = pd.concat(frames, ignore_index=True).drop_duplicates(["accn", "owner", "trans_date", "shares", "price"])
        return out.assign(symbol=out["issuer_cik"].astype(int).map(by_cik))

    out = edgar.cached_table("insiders", build, use_cache)
    return out.assign(owner=out["owner"].fillna("").astype(str))


def panels(purchases: pd.DataFrame, filings: pd.DataFrame, index: pd.DatetimeIndex, symbols: list[str]) -> dict:
    idx = pd.DatetimeIndex(index)
    acc = filings.drop_duplicates("accessionNumber").set_index("accessionNumber")["acceptanceDateTime"]
    p = purchases[purchases["symbol"].isin(symbols)].copy()
    p["bar"] = edgar.available_bar(edgar.acceptance_times(p["accn"].map(acc)), p["filed"], idx)
    p["value"] = (p["shares"] * p["price"]).fillna(0.0)
    p = p.dropna(subset=["bar"])
    buyers = pd.DataFrame(0.0, index=index, columns=symbols)
    value = pd.DataFrame(0.0, index=index, columns=symbols)
    day = pd.Series(idx, index=idx)
    for (s, _owner), g in p.groupby(["symbol", "owner"]):
        last = pd.Series(pd.NaT, index=idx, dtype="datetime64[ns]")
        last[pd.DatetimeIndex(g["bar"].unique())] = pd.DatetimeIndex(g["bar"].unique())
        active = (day - last.ffill()) < WINDOW
        buyers[s] += active.to_numpy(dtype=float)
    if len(p):
        daily = p.groupby(["bar", "symbol"])["value"].sum().unstack().reindex(index=idx, columns=symbols).fillna(0.0)
        value.loc[:, :] = daily.rolling(WINDOW).sum().clip(lower=0.0).to_numpy()
    return {"insider_buyers": buyers, "insider_buy_value": value}


def synthetic_purchases(symbols: list[str], start="2014-01-01", end="2026-06-30", seed=23) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Random sparse purchases and matching filing rows (acceptance before or after the close)."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(start, end)
    rows, fil = [], []
    for i, s in enumerate(symbols):
        for k in range(int(rng.integers(5, 40))):
            filed = days[int(rng.integers(0, len(days)))]
            accn = f"S{i:03d}-{k:05d}"
            rows.append({"accn": accn, "issuer_cik": i + 1, "owner": str(int(rng.integers(1, 8))),
                         "filed": f"{filed:%Y-%m-%d}", "trans_date": f"{filed - pd.Timedelta(days=2):%Y-%m-%d}",
                         "shares": float(rng.integers(100, 20000)), "price": float(rng.uniform(20, 400)), "symbol": s})
            fil.append({"accessionNumber": accn, "acceptanceDateTime": f"{filed:%Y-%m-%d}T{'15:10:00' if k % 2 else '22:20:00'}.000Z"})
    return pd.DataFrame(rows), pd.DataFrame(fil)
