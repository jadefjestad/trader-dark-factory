# Intraday data on the free Alpaca plan

Measured by `python -m factory.intraday_probe` (workflow `probe-sources`) on 2026-10-04, over the
25-stock universe and the sessions 2026-09-30 to 2026-10-02. Issue #67.

## Measurements

| Question | Result |
|---|---|
| IEX share of all-exchange (SIP) volume | median 5.4% (3.4% to 8.7% by symbol) |
| Regular-session minutes with an IEX bar | median 94% (65% for the thinnest name, 100% for the busiest) |
| Gap between IEX and SIP 1-minute closes | median 0.8 bps; 95th percentile 4.7 bps (11 bps worst symbol) |
| SIP bars from the last 15 minutes | refused (403: "subscription does not permit querying recent SIP data") |
| 1-minute history depth | SIP from 2016-01; IEX from 2020-07 |
| Data API rate limit | 200 requests a minute |
| IEX quoted spreads | not measured yet: the probe ran on a weekend, when stale quotes give meaningless spreads. Rerun during market hours. |

## What this means

- **True high-frequency trading is out.** Live data is one exchange carrying about 5% of volume, paper
  fills are simulated, and there is no order-book queue to compete in.
- **Intraday trading on 5 to 15 minute bars is workable.** IEX minute prices track the consolidated
  market closely (under 1 bp typically, about 5 bps in the tails), so signals computed live from IEX
  bars differ little from signals on SIP bars. 1-minute bars are less reliable: about 6% of minutes
  have no IEX trade, and up to a third for the thinnest names.
- **Backtest on SIP, trade on IEX signals, and charge for the difference.** Historical SIP minute bars
  are free once they are older than 15 minutes, with ten years of history. The intraday backtester
  (#68) should use SIP bars, stamp each bar with its availability time, and add a feed-mismatch
  buffer of at least the measured 95th-percentile gap (about 5 bps per trade) on top of spread and
  slippage.
- **Rate limits are fine** for polling 25 symbols every few minutes (one multi-symbol request per poll).

## Tiingo and Twelve Data

Not probed yet: no keys are configured, and the probe reports them as "not configured". From their
published free tiers (to be confirmed by the probe if keys are added):

- **Tiingo's free intraday feed is IEX data**, the same exchange Alpaca's free real-time feed uses, so
  it adds redundancy but not better coverage.
- **Twelve Data's free tier is limited to a few requests a minute and a daily cap**, too few to refresh
  25 symbols every minute through a session.

Verdict: neither beats Alpaca for this use today, so the factory does not ask for their keys. The
data layer stays pluggable (#68), and the probe already tests both the moment
`TIINGO_API_KEY` or `TWELVEDATA_API_KEY` exists as a repository secret.
