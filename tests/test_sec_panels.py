import io
import zipfile

import numpy as np
import pandas as pd
import pytest

from factory import earnings, edgar, extras, fundamentals, insiders
from factory.data import DataError, synthetic

BARS = pd.DatetimeIndex(pd.bdate_range("2024-03-04", "2024-03-15"))   # Mon 4th .. Fri 15th


def test_acceptance_before_close_counts_same_day_after_close_next_day():
    # EDGAR times are UTC; New York is UTC-5 in early March 2024
    acc = pd.Series(["2024-03-05T12:30:00.000Z", "2024-03-05T21:00:00.000Z", "2024-03-05T21:01:00.000Z",
                     "2024-03-08T23:00:00.000Z", "", "2024-03-06T03:00:00.000Z"])
    filed = pd.Series(["2024-03-05", "2024-03-05", "2024-03-05", "2024-03-08", "2024-03-06", "2024-03-05"])
    bars = edgar.available_bar(edgar.acceptance_times(acc), filed, BARS)
    assert [str(b.date()) for b in bars] == ["2024-03-05", "2024-03-05", "2024-03-06",
                                             "2024-03-11",   # Friday evening -> Monday
                                             "2024-03-07",   # no acceptance time: the bar after the filing date
                                             "2024-03-06"]   # 22:00 New York time on the 5th


def test_missing_contact_fails_closed(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(DataError):
        edgar.get("https://data.sec.gov/submissions/CIK0000320193.json")


# ---------------------------------------------------------------- fundamentals

def _facts(rows_by_tag):
    return {"facts": {"us-gaap": {tag: {"units": {unit: rows}} for tag, (unit, rows) in rows_by_tag.items()}}}


def test_first_filed_value_wins_and_q4_is_derived_at_the_annual_filing():
    eps = [
        {"start": "2023-01-01", "end": "2023-03-31", "val": 1.0, "accn": "q1", "filed": "2023-05-01"},
        {"start": "2023-04-01", "end": "2023-06-30", "val": 1.1, "accn": "q2", "filed": "2023-08-01"},
        {"start": "2023-07-01", "end": "2023-09-30", "val": 1.2, "accn": "q3", "filed": "2023-11-01"},
        {"start": "2023-01-01", "end": "2023-12-31", "val": 4.6, "accn": "k", "filed": "2024-02-01"},
        # comparative restated in a later filing: ignored
        {"start": "2023-01-01", "end": "2023-03-31", "val": 9.0, "accn": "q1b", "filed": "2024-05-01"},
    ]
    q = fundamentals.quarterize(fundamentals.extract(_facts({"EarningsPerShareDiluted": ("USD/shares", eps)})))
    q = q[q["metric"] == "eps"].sort_values("end")
    assert q["val"].round(6).tolist() == [1.0, 1.1, 1.2, 1.3]
    assert q.iloc[-1][["accn", "filed"]].tolist() == ["k", "2024-02-01"]


def test_gross_profit_falls_back_to_revenue_minus_cost():
    rev = [{"start": "2023-01-01", "end": "2023-03-31", "val": 100.0, "accn": "a", "filed": "2023-05-01"}]
    cogs = [{"start": "2023-01-01", "end": "2023-03-31", "val": 60.0, "accn": "a", "filed": "2023-05-01"}]
    q = fundamentals.quarterize(fundamentals.extract(_facts({"Revenues": ("USD", rev), "CostOfRevenue": ("USD", cogs)})))
    assert q[q["metric"] == "gross_profit"]["val"].tolist() == [40.0]


def test_fundamental_values_appear_only_once_filed():
    idx = pd.DatetimeIndex(pd.bdate_range("2020-01-01", "2026-06-30"))
    table = fundamentals.synthetic_table(["AAPL"])
    fil = fundamentals.synthetic_filings(table)
    p = fundamentals.panels(table, fil, idx, ["AAPL"])["eps_ttm"]["AAPL"]
    t = fundamentals.with_bars(table, fil, idx)
    eps = t[t["metric"] == "eps"].dropna(subset=["bar"])
    for b in sorted(eps["bar"].unique())[5:12]:
        b = pd.Timestamp(b)
        before = idx[idx.get_loc(b) - 1]
        known = eps[eps["bar"] <= before].sort_values("end").tail(4)
        assert p[before] == pytest.approx(known["val"].sum())
        assert p[b] != pytest.approx(known["val"].sum()) or eps[eps["bar"] == b]["val"].sum() == 0


def test_stale_fundamentals_become_nan():
    idx = pd.DatetimeIndex(pd.bdate_range("2014-01-01", "2026-06-30"))
    table = fundamentals.synthetic_table(["AAPL"])
    table = table[pd.to_datetime(table["end"]) < "2020-01-01"]          # company stops reporting
    p = fundamentals.panels(table, fundamentals.synthetic_filings(table), idx, ["AAPL"])["eps_ttm"]["AAPL"]
    assert p.loc["2020-03-02":"2020-06-01"].notna().all()
    assert p.loc["2021-01-04":].isna().all()


# ---------------------------------------------------------------- insiders

FORM4 = b"""<?xml version="1.0"?>
<ownershipDocument>
  <reportingOwner><reportingOwnerId><rptOwnerCik>0001234567</rptOwnerCik></reportingOwnerId></reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <transactionDate><value>2024-03-01</value></transactionDate>
      <transactionCoding><transactionCode>P</transactionCode></transactionCoding>
      <transactionAmounts><transactionShares><value>1000</value></transactionShares>
        <transactionPricePerShare><value>50.5</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode></transactionAmounts>
    </nonDerivativeTransaction>
    <nonDerivativeTransaction>
      <transactionDate><value>2024-03-01</value></transactionDate>
      <transactionCoding><transactionCode>S</transactionCode></transactionCoding>
      <transactionAmounts><transactionShares><value>500</value></transactionShares>
        <transactionPricePerShare><value>51</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>D</value></transactionAcquiredDisposedCode></transactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>"""


def test_form4_keeps_only_open_market_purchases():
    rows = insiders.parse_form4(FORM4, "0001-24-1", 320193, "2024-03-04")
    assert len(rows) == 1
    assert rows[0]["owner"] == "1234567" and rows[0]["shares"] == 1000 and rows[0]["price"] == 50.5


def _tsv(rows):
    return pd.DataFrame(rows).to_csv(sep="\t", index=False)


def test_dataset_parse_filters_issuer_code_and_amendments():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("SUBMISSION.tsv", _tsv([
            {"ACCESSION_NUMBER": "a1", "FILING_DATE": "05-MAR-2024", "DOCUMENT_TYPE": "4", "ISSUERCIK": "320193"},
            {"ACCESSION_NUMBER": "a2", "FILING_DATE": "06-MAR-2024", "DOCUMENT_TYPE": "4/A", "ISSUERCIK": "320193"},
            {"ACCESSION_NUMBER": "a3", "FILING_DATE": "06-MAR-2024", "DOCUMENT_TYPE": "4", "ISSUERCIK": "999"}]))
        z.writestr("NONDERIV_TRANS.tsv", _tsv([
            {"ACCESSION_NUMBER": a, "TRANS_CODE": c, "TRANS_ACQUIRED_DISP_CD": d, "TRANS_DATE": "01-MAR-2024",
             "TRANS_SHARES": "100", "TRANS_PRICEPERSHARE": "10"}
            for a, c, d in (("a1", "P", "A"), ("a1", "S", "D"), ("a2", "P", "A"), ("a3", "P", "A"))]))
        z.writestr("REPORTINGOWNER.tsv", _tsv([{"ACCESSION_NUMBER": a, "RPTOWNERCIK": "0042"} for a in ("a1", "a2", "a3")]))
    df = insiders.parse_dataset(buf.getvalue(), {320193})
    assert df[["accn", "issuer_cik", "owner", "filed", "trans_date"]].values.tolist() == [
        ["a1", 320193, "42", "2024-03-05", "2024-03-01"]]


def test_insider_window_counts_distinct_buyers_from_acceptance():
    idx = pd.DatetimeIndex(pd.bdate_range("2024-01-01", "2024-08-30"))
    p = pd.DataFrame([{"accn": "x1", "owner": "1", "filed": "2024-03-05", "shares": 10.0, "price": 10.0, "symbol": "AAPL"},
                      {"accn": "x2", "owner": "1", "filed": "2024-03-06", "shares": 10.0, "price": 10.0, "symbol": "AAPL"},
                      {"accn": "x3", "owner": "2", "filed": "2024-03-06", "shares": 10.0, "price": 10.0, "symbol": "AAPL"}])
    f = pd.DataFrame({"accessionNumber": ["x1", "x2", "x3"],
                      "acceptanceDateTime": ["2024-03-05T22:00:00.000Z", "2024-03-06T13:00:00.000Z", "2024-03-06T13:00:00.000Z"]})
    out = insiders.panels(p, f, idx, ["AAPL", "MSFT"])
    b = out["insider_buyers"]["AAPL"]
    assert b["2024-03-05"] == 0          # accepted after the close
    assert b["2024-03-06"] == 2          # two distinct insiders
    assert b["2024-06-03"] == 2 and b["2024-06-05"] == 0     # 90 calendar days later the window closes
    assert out["insider_buy_value"]["AAPL"]["2024-03-06"] == pytest.approx(300.0)
    assert (out["insider_buyers"]["MSFT"] == 0).all()


# ---------------------------------------------------------------- earnings

def test_announcements_drop_corrections():
    ev = earnings.announcements(earnings.synthetic_filings(["AAPL"], "2020-01-01", "2021-12-31"))
    assert len(ev) == 8
    assert not ev["accessionNumber"].str.endswith("c").any()


def test_reaction_window_depends_on_release_time():
    idx = pd.DatetimeIndex(pd.bdate_range("2024-03-04", "2024-03-15"))
    close = pd.DataFrame({"AAPL": np.arange(100.0, 110.0), "MSFT": np.full(10, 50.0)}, index=idx)
    close.loc["2024-03-07", "AAPL"] = 120.0
    ev = pd.DataFrame({"symbol": ["AAPL"], "accessionNumber": ["e"], "filingDate": ["2024-03-06"],
                       "acceptanceDateTime": ["2024-03-06T21:30:00.000Z"]})   # after the close: bar = Thu 7th
    out = earnings.panels(ev, close)
    r = out["earnings_reaction"]["AAPL"]
    assert r[:"2024-03-07"].isna().all()                       # not known until the close after the bar
    expect = (close.loc["2024-03-08", "AAPL"] / close.loc["2024-03-06", "AAPL"] - 1) / 2   # minus the equal-weight mean
    assert r["2024-03-08"] == pytest.approx(expect)
    assert r["2024-03-15"] == pytest.approx(expect)
    assert out["earnings_age"]["AAPL"]["2024-03-08"] == 0 and out["earnings_age"]["AAPL"]["2024-03-12"] == 2
    ev.loc[0, "acceptanceDateTime"] = "2024-03-06T12:00:00.000Z"           # before the open: bar = Wed 6th
    r2 = earnings.panels(ev, close)["earnings_reaction"]["AAPL"]
    assert r2["2024-03-06"] != r2["2024-03-06"] and r2["2024-03-07"] == r2["2024-03-07"]


# ---------------------------------------------------------------- panels through extras

ALL = ["gross_profitability", "eps_ttm", "eps_sue", "insider_buyers", "insider_buy_value",
       "earnings_reaction", "earnings_age"]


def test_sec_panels_are_causal_on_truncated_data():
    md = synthetic(["AAPL", "MSFT", "JPM"], start="2016-01-01", end="2024-12-31")
    full = extras.attach(md, ALL, "synthetic").extra
    cut = md.index[1500]
    part = extras.attach(md.slice(None, cut), ALL, "synthetic").extra
    for n in ALL:
        pd.testing.assert_frame_equal(part[n], full[n].loc[:cut], check_freq=False, obj=n)
        assert full[n].shape == md.close.shape


def test_sec_panels_follow_symbol_selection():
    md = extras.attach(synthetic(["AAPL", "MSFT", "SPY"], start="2023-01-01", end="2024-06-01"), ["eps_sue"], "synthetic")
    assert list(md.select(["MSFT"]).extra["eps_sue"].columns) == ["MSFT"]


def test_evaluate_workflow_fetches_every_panel():
    """The plan job greps candidates for panel names; a panel missing there would never be downloaded."""
    from pathlib import Path
    text = (Path(__file__).resolve().parent.parent / ".github/workflows/evaluate.yml").read_text()
    line = next(x for x in text.splitlines() if "for n in news_count" in x)
    assert set(extras.PANELS) <= set(line.replace(";", " ").split())


def test_insider_fetch_reuses_the_days_cache_without_network(tmp_path, monkeypatch):
    """The evaluate job has no SEC access; it must read what the data job cached that day."""
    monkeypatch.setattr(edgar, "CACHE_DIR", tmp_path)
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    pd.DataFrame([{"accn": "a", "issuer_cik": 320193, "owner": "42", "filed": "2024-03-05", "trans_date": "2024-03-01",
                   "shares": 1.0, "price": 2.0, "symbol": "AAPL"}]).to_csv(edgar.daily_cache("insiders"), index=False)
    out = insiders.fetch(["AAPL"], pd.DataFrame())
    assert out["symbol"].tolist() == ["AAPL"] and out["owner"].tolist() == ["42"]
