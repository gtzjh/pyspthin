"""Small benchmark harness for pyspthin."""

from __future__ import annotations

import random
import time

import pandas as pd
import psutil

from pyspthin import thin


def make_dataset(seed: int, n_points: int, species: str = "bench-sp") -> pd.DataFrame:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    for index in range(n_points):
        rows.append(
            {
                "SPEC": species,
                "LONG": rng.uniform(-20.0, 20.0),
                "LAT": rng.uniform(-20.0, 20.0),
                "OBS_ID": f"{species}-{index}",
                "SOURCE": "benchmark",
            }
        )
    return pd.DataFrame.from_records(rows)


def main() -> None:
    process = psutil.Process()
    scenarios = [
        ("small", 100, 100.0, 10),
        ("medium", 500, 75.0, 10),
        ("large", 1000, 50.0, 10),
    ]

    print("name,n_points,thin_par,reps,elapsed_seconds,edge_count,max_retained,rss_bytes")
    for name, n_points, thin_par, reps in scenarios:
        data = make_dataset(seed=100 + n_points, n_points=n_points)
        started = time.perf_counter()
        result = thin(data, thin_par=thin_par, reps=reps, seed=123, n_jobs=1)
        elapsed = time.perf_counter() - started
        rss_bytes = process.memory_info().rss
        print(
            f"{name},{n_points},{thin_par},{reps},{elapsed:.6f},"
            f"{result.graph_stats.edge_count},{result.best_replicate.retained_count},{rss_bytes}"
        )


if __name__ == "__main__":
    main()
