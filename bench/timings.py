"""Summarise the timings in a run.lua results file.

    python3 timings.py results-corpus.txt
"""
import statistics
import sys

ALGOS = ["stock", "upstream", "invertfix", "patched"]


def load(path):
    times = {algo: [] for algo in ALGOS}
    try:
        with open(path, encoding="utf-8") as f:
            rows = f.read().splitlines()
    except OSError as exc:
        sys.exit(f"cannot read {path}: {exc}")
    for line in rows:
        parts = line.strip().split("|")
        if len(parts) < 3 or parts[1] not in times:
            continue
        try:
            times[parts[1]].append(float(parts[-1]))
        except ValueError:
            continue
    return times


def pct(values, q):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "results.txt"
    times = load(path)
    base = statistics.median(times["stock"]) if times["stock"] else 0.0
    prev = statistics.median(times["invertfix"]) if times["invertfix"] else 0.0

    print(f"{'algo':10} {'n':>4} {'median':>8} {'mean':>8} {'p90':>8} {'vs stock':>9} {'vs prev':>8}")
    for algo in ALGOS:
        values = times[algo]
        if not values:
            continue
        median = statistics.median(values)
        print(f"{algo:10} {len(values):4d} {median:8.1f} {statistics.mean(values):8.1f} "
              f"{pct(values, 0.9):8.1f} {median / base * 100:8.0f}% {median / prev * 100:7.0f}%")


if __name__ == "__main__":
    main()
