"""Download and cache every dataset the evaluator needs (run in the job that holds the Alpaca keys)."""
import sys

from factory import config
from factory.evaluate import load_data


def main() -> int:
    cfg = config.evaluation()
    for tf in cfg["periods"]:
        md, bench = load_data(tf, "alpaca", cfg)
        print(f"{tf}: {len(md.index)} bars, {md.index[0]} to {md.index[-1]}, source {md.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
