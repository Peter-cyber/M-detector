#!/usr/bin/env python3
import argparse
import statistics


COLUMNS = [
    ("points", 0),
    ("detect_s", 1),
    ("cluster_s", 2),
    ("push_s", 3),
    ("push_depth_s", 4),
]


def percentile(values, ratio):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * ratio))))
    return ordered[index]


def main():
    parser = argparse.ArgumentParser(description="Summarize DynObjFilter time_file output.")
    parser.add_argument("time_file")
    parser.add_argument("--label", default="")
    parser.add_argument("--warmup", type=int, default=5)
    args = parser.parse_args()

    rows = []
    with open(args.time_file, "r", encoding="utf-8") as handle:
        for line in handle:
            values = [float(value) for value in line.split()]
            if len(values) >= len(COLUMNS):
                rows.append(values[: len(COLUMNS)])

    measured = rows[args.warmup :] if len(rows) > args.warmup else rows
    label = f"{args.label} " if args.label else ""
    print(f"{label}frames={len(rows)} measured={len(measured)} warmup={min(args.warmup, len(rows))}")
    if not measured:
        return

    for name, index in COLUMNS:
        values = [row[index] for row in measured]
        if name == "points":
            print(f"{label}{name}: mean={statistics.mean(values):.0f}")
        else:
            print(
                f"{label}{name}: mean={statistics.mean(values):.6f}s "
                f"p50={statistics.median(values):.6f}s p95={percentile(values, 0.95):.6f}s"
            )


if __name__ == "__main__":
    main()
