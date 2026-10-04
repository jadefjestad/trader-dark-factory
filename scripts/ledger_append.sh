#!/usr/bin/env bash
# Append files to the `ledger` branch (append-only record of every experiment and execution). PROTECTED.
# usage: scripts/ledger_append.sh <subdir> <message> <file>...
set -euo pipefail
subdir="$1"; msg="$2"; shift 2
work="$(mktemp -d)"
repo="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
if git ls-remote --exit-code --heads "$repo" ledger >/dev/null 2>&1; then
  git clone --quiet --depth 1 --branch ledger "$repo" "$work"
else
  git init --quiet -b ledger "$work"
  git -C "$work" remote add origin "$repo"
  printf '# Ledger\n\nAppend-only record written by GitHub Actions: every experiment (passed or failed) and every execution run.\n' > "$work/README.md"
fi
mkdir -p "$work/$subdir"
for f in "$@"; do
  cp "$f" "$work/$subdir/"
  if [[ "$f" == *.json ]]; then
    python3 -c "import json,sys; r=json.load(open(sys.argv[1])); print(json.dumps({k:r.get(k) for k in ('experiment_id','evaluated_at','score','passed_gates','beats_champion','promote','status','started_at')}|({'strategy':r['strategy']['name']} if 'strategy' in r else {})))" "$f" >> "$work/$subdir/index.jsonl"
  fi
done
cd "$work"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit --quiet -m "$msg"
for i in 1 2 3 4; do
  git push --quiet origin ledger && exit 0
  sleep $((i * 3)); git pull --quiet --rebase origin ledger
done
echo "ledger push failed" >&2; exit 1
