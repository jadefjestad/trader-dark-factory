# Running the streamer on Azure (optional, nothing is provisioned)

Held until a 5 to 15 minute strategy passes the intraday backtester (Jade, 2026-10-04). This page lists
exactly what would be needed then. Design: `docs/streaming-design.md`; code: `factory/stream/`,
`deploy/streamer/`.

## What Jade would create
1. A **second Alpaca paper account** (same login) used only by the streamer, and its paper key pair.
   The streamer refuses any account whose number doesn't start with `PA`, and any non-paper endpoint.
2. A resource group in **East US** with a **Container Apps environment** and one **scheduled Container
   Apps Job**: weekdays, start 09:20 New York, replica timeout about 7 hours, 0.25 vCPU / 0.5 GiB.
   Expected cost about $0 inside the monthly free grant (check the Azure pricing calculator).
3. Two secrets on the job: `ALPACA_API_KEY_ID` and `ALPACA_API_SECRET_KEY` (the streaming paper account).
4. Image: `ghcr.io/jadefjestad/trader-dark-factory-streamer` (GHCR is free for a public repo), built from
   `deploy/streamer/Dockerfile`. A build workflow is added when the job exists.
5. A storage account with a `ledger-stream` container for the JSON-lines logs (managed identity for the
   job, a read-only SAS as GitHub secret `AZURE_LEDGER_SAS` so Actions can copy logs into the ledger).

No GitHub write credential ever lives in Azure, and nothing here can trade live.

## Behaviour once running
- Shadow mode unless `STREAM_SUBMIT=1` **and** the stream champion's timeframe is in the protected
  `executable_timeframes`. Today no streaming timeframe is, so it can only log what it would do.
- Limits come from the `stream:` section of `protected/risk_limits.yaml`.
- `/healthz` answers 503 when the loop stops ticking, so the platform restarts it.
- Without `state/champion_stream.json` it runs a flat strategy: a smoke test of feed, bars and logs.
