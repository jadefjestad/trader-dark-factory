#!/usr/bin/env bash
# Append files to the `ledger` branch (append-only record of every experiment and execution). PROTECTED.
# usage: scripts/ledger_append.sh <subdir> <message> <file>...
# Each attempt starts from a fresh clone of the ledger tip, so concurrent writers never hit rebase
# conflicts; an existing file is never overwritten.
set -euo pipefail
subdir="$1"; msg="$2"; shift 2
repo="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"

attempt_append() {
  local work; work="$(mktemp -d)"
  if git ls-remote --exit-code --heads "$repo" ledger >/dev/null 2>&1; then
    git clone --quiet --depth 1 --branch ledger "$repo" "$work"
  else
    git init --quiet -b ledger "$work"
    git -C "$work" remote add origin "$repo"
    printf '# Ledger\n\nAppend-only record written by GitHub Actions: every experiment (passed or failed) and every execution run.\n' > "$work/README.md"
  fi
  mkdir -p "$work/$subdir"
  for f in "$@"; do
    dest="$work/$subdir/$(basename "$f")"
    if [ -e "$dest" ]; then echo "ledger already has $subdir/$(basename "$f"); refusing to overwrite" >&2; return 2; fi
    cp "$f" "$dest"
    if [[ "$f" == *.json ]]; then
      python3 -c "import json,sys; r=json.load(open(sys.argv[1])); print(json.dumps({k:r.get(k) for k in ('experiment_id','evaluated_at','passed_gates','beats_champion','promote','status','started_at')}|({'strategy':r['strategy']['name']} if 'strategy' in r else {})))" "$f" >> "$work/$subdir/index.jsonl"
    fi
  done
  git -C "$work" config user.name "github-actions[bot]"
  git -C "$work" config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git -C "$work" add -A
  git -C "$work" commit --quiet -m "$msg"
  git -C "$work" push --quiet origin ledger
}

for i in 1 2 3 4 5; do
  set +e; attempt_append "$@"; rc=$?; set -e
  [ "$rc" -eq 0 ] && exit 0
  [ "$rc" -eq 2 ] && exit 2
  sleep $((i * 3))
done
echo "ledger push failed after retries" >&2; exit 1
