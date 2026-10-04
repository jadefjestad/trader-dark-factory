"""Decide the PR check result from evaluation outputs. PROTECTED.

    python scripts/pr_verdict.py --results results/ --head-champion pr_champion.json --base-champion state/champion.json

Fails when a candidate could not be evaluated, or when the PR changes state/champion.json without a
matching evaluation that says PROMOTE. Writes verdict.md for the PR comment.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

KEYS = ("ref", "params", "code_sha256", "timeframe")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--head-champion", required=True)
    ap.add_argument("--base-champion", required=True)
    ap.add_argument("--head-root", required=True, help="checkout of the PR head, read for champion code only")
    ap.add_argument("--errors", default="")
    ap.add_argument("--out", default="verdict.md")
    a = ap.parse_args()
    results = [json.loads(p.read_text()) for p in sorted(Path(a.results).glob("*.json"))]
    head = json.loads(Path(a.head_champion).read_text())
    base = json.loads(Path(a.base_champion).read_text())
    lines, ok = [], True

    errors = Path(a.errors).read_text().strip() if a.errors and Path(a.errors).exists() else ""
    if errors:
        ok = False
        lines += ["### Evaluation errors", "```", errors[-3000:], "```"]

    for r in results:
        lines.append((Path(a.results) / f"{r['experiment_id']}.md").read_text())

    # whatever the manifest says, the code it points to must exist at the PR head with the recorded hash
    if head["ref"].endswith(".py"):
        path = Path(a.head_root) / head["ref"]
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != head.get("code_sha256"):
            ok = False
            lines.append(f"**Champion code check failed**: `{head['ref']}` is missing, a symlink, or no longer matches "
                         "the hash in `state/champion.json`. Merging would stop scheduled trading.")

    if {k: head.get(k) for k in KEYS} != {k: base.get(k) for k in KEYS}:
        match = [r for r in results if r["promote"] and all(
            head.get(k) == r["strategy"][k] for k in KEYS)]
        if match:
            lines.append(f"**Promotion verified**: `{head['ref']}` passed every gate and beat the champion. Merging promotes it.")
        else:
            ok = False
            lines.append("**Promotion rejected**: this PR changes `state/champion.json` but no evaluation in this run says PROMOTE for exactly that strategy, params and code hash.")
    else:
        for r in results:
            if r["promote"]:
                champ = {"ref": r["strategy"]["ref"], "params": r["strategy"]["params"], "name": r["strategy"]["name"],
                         "timeframe": r["strategy"]["timeframe"], "code_sha256": r["strategy"]["code_sha256"],
                         "experiment_id": r["experiment_id"], "promoted_at": r["evaluated_at"]}
                lines += [f"To promote `{r['strategy']['name']}`, commit this as `state/champion.json` on this branch:",
                          "```json", json.dumps(champ, indent=2), "```"]
    if not results and not errors:
        lines.append("No candidate strategy or champion change in this PR; nothing to evaluate.")
    Path(a.out).write_text("\n\n".join(lines) + "\n")
    print("\n\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
