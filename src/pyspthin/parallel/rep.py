"""Replicate-level parallel execution."""

from __future__ import annotations

import multiprocessing as mp
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from pyspthin.algorithm.runner import ReplicateExecution, execute_replicate
from pyspthin.graph.conflict_graph import ConflictGraph


def _best_mp_context() -> mp.context.BaseContext:
    available = mp.get_all_start_methods()
    method = "fork" if "fork" in available else available[0]
    return mp.get_context(method)


def run_replicates(
    graph: ConflictGraph,
    seeds: list[int],
    n_jobs: int,
) -> list[ReplicateExecution]:
    if n_jobs <= 1 or len(seeds) <= 1:
        return [execute_replicate(graph, seed, index) for index, seed in enumerate(seeds, start=1)]

    try:
        with ProcessPoolExecutor(max_workers=n_jobs, mp_context=_best_mp_context()) as executor:
            futures = [
                executor.submit(execute_replicate, graph, seed, index)
                for index, seed in enumerate(seeds, start=1)
            ]
            return [future.result() for future in futures]
    except Exception as exc:  # pragma: no cover - exercised only on platform-specific failures
        warnings.warn(
            "Falling back to threaded replicate execution because process parallelism "
            f"failed: {exc}",
            stacklevel=2,
        )
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            futures = [
                executor.submit(execute_replicate, graph, seed, index)
                for index, seed in enumerate(seeds, start=1)
            ]
            return [future.result() for future in futures]
