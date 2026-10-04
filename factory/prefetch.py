"""Download and cache the datasets the evaluator needs (run in the job that holds the Alpaca keys).

    python -m factory.prefetch --timeframes 1Day,15Min [--extra news_count]
"""
import argparse
import sys
import time

from factory import config, extras
from factory.evaluate import load_data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeframes", default="1Day", help="comma-separated, e.g. 1Day,15Min")
    ap.add_argument("--extra", default="", help="comma-separated extra panels to cache for daily data")
    a = ap.parse_args(argv)
    cfg = config.evaluation()
    for tf in [t for t in a.timeframes.split(",") if t]:
        if tf not in cfg["periods"]:
            print(f"no evaluation periods defined for {tf}", file=sys.stderr)
            return 2
        t0 = time.time()
        md, _ = load_data(tf, "alpaca", cfg)
        names = [x for x in a.extra.split(",") if x]
        if tf == "1Day" and names:
            md = extras.attach(md, names, "alpaca")
        print(f"{tf}: {len(md.index)} bars, {md.index[0]} to {md.index[-1]}, source {md.source}, {time.time() - t0:.0f}s",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
