"""Logging utilities for pyspthin."""

from __future__ import annotations

from pathlib import Path

from pyspthin.models import ThinResult


def build_log_lines(result: ThinResult) -> list[str]:
    counts = [rep.retained_count for rep in result.replicates]
    return [
        f"Species: {result.species}",
        f"Started at: {result.started_at.isoformat()}",
        f"Ended at: {result.ended_at.isoformat()}",
        f"Elapsed seconds: {result.elapsed_seconds:.6f}",
        f"Threshold (km): {result.config['thin_par']}",
        f"Replicates: {result.config['reps']}",
        f"Seed: {result.config['seed']}",
        f"n_jobs: {result.config['n_jobs']}",
        f"Maximum retained count: {result.best_replicate.retained_count}",
        f"Retained counts: {counts}",
        f"Conflict edges: {result.graph_stats.edge_count}",
        f"Estimated adjacency bytes: {result.graph_stats.estimated_bytes}",
    ]


def write_log(path: Path, result: ThinResult) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(build_log_lines(result)) + "\n")
    return path

