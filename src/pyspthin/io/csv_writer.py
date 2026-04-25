"""CSV output helpers."""

from __future__ import annotations

from pathlib import Path

from pyspthin.models import ThinResult


def write_best_replicates_to_csv(result: ThinResult, out_dir: Path, out_base: str, max_files: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    max_retained = result.best_replicate.retained_count
    best_replicates = [rep for rep in result.replicates if rep.retained_count == max_retained]
    written_paths: list[Path] = []

    for index, replicate in enumerate(best_replicates[:max_files], start=1):
        path = out_dir / f"{out_base}_thin{index}.csv"
        replicate.retained_dataframe.to_csv(path, index=False)
        written_paths.append(path)

    return written_paths
