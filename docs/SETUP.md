# One-time setup (Jade)

## 1. Alpaca secrets
Repo → Settings → Secrets and variables → Actions → **New repository secret**:

| Name | Value |
|---|---|
| `ALPACA_API_KEY_ID` | your **paper** API key id |
| `ALPACA_API_SECRET_KEY` | your **paper** API secret |

Never put keys in files. The executor refuses accounts whose number does not start with `PA`.

Optional variable (same page, **Variables** tab): `AUTO_PROMOTE` = `true` lets a PR that passes the
promotion verdict auto-merge itself. Leave unset to merge promotions by hand.

## 2. Actions permissions
Settings → Actions → General:
- Workflow permissions: **Read and write permissions** (the ledger branch and PR comments need it).
- Tick **Allow GitHub Actions to create and approve pull requests** only if you use `AUTO_PROMOTE`.

## 3. Branch protection for `main`
Settings → Branches → Add rule (or Rules → Rulesets) for `main`:
- Require a pull request before merging; **Require review from Code Owners**.
- Require status checks: `ci / test` and `evaluate / report`.

Note: GitHub Free does not enforce branch protection on **private** repos. Until the repo is public (or
you have GitHub Pro), CODEOWNERS and required checks are advisory; the CI guard and the base-branch
evaluator still run and still fail the checks.

## 4. The research Routine
claude.ai/code → Routines → New:
- Repository: `jadefjestad/trader-dark-factory`
- Prompt: the block in `agent/ROUTINE.md` (it already points at issue #2, "Factory usage log")
- Schedule: as often as your plan allows (for example every 2 hours on weekdays). The budget in
  `agent/usage_policy.yaml` makes surplus runs exit immediately; set `max_runs_per_day` to your plan's
  daily Routine cap.

## 5. First runs
1. Actions → **evaluate** → Run workflow with the candidate blank: baseline leaderboard on real data,
   recorded on the `ledger` branch.
2. Actions → **execute** → Run workflow with dry run ticked: shows the orders it would place.
3. The scheduled **execute** job then trades the champion (seeded as equal-weight buy-and-hold)
   every weekday after the open.
