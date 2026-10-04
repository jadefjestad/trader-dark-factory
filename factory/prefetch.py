"""Download and cache the datasets the evaluator needs (run in the job that holds the Alpaca keys).

    python -m factory.prefetch --timeframes 1Day,15Min
"""
import argparse
import sys
import time

from factory import config
from factory.evaluate import load_data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeframes", default="1Day", help="comma-separated, e.g. 1Day,15Min")
    a = ap.parse_args(argv)
    cfg = config.evaluation()
    for tf in [t for t in a.timeframes.split(",") if t]:
        if tf not in cfg["periods"]:
            print(f"no evaluation periods defined for {tf}", file=sys.stderr)
            return 2
        t0 = time.time()
        md, _ = load_data(tf, "alpaca", cfg)
        print(f"{tf}: {len(md.index)} bars, {md.index[0]} to {md.index[-1]}, source {md.source}, {time.time() - t0:.0f}s",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
