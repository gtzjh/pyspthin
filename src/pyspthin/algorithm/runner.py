"""Replicate execution helpers."""

from __future__ import annotations

import time
from dataclasses import dataclass

from pyspthin.algorithm.greedy import run_greedy_replicate
from pyspthin.graph.conflict_graph import ConflictGraph


@dataclass(frozen=True, slots=True)
class ReplicateExecution:
    """Internal representation of one replicate before row restoration."""

    replicate_id: int
    seed: int
    retained_indices: list[int]
    retained_count: int
    elapsed_seconds: float


def execute_replicate(graph: ConflictGraph, seed: int, replicate_id: int) -> ReplicateExecution:
    started = time.perf_counter()
    retained_indices = run_greedy_replicate(graph, seed)
    elapsed_seconds = time.perf_counter() - started
    return ReplicateExecution(
        replicate_id=replicate_id,
        seed=seed,
        retained_indices=retained_indices,
        retained_count=len(retained_indices),
        elapsed_seconds=elapsed_seconds,
    )


def sort_executions(executions: list[ReplicateExecution]) -> list[ReplicateExecution]:
    return sorted(executions, key=lambda item: (-item.retained_count, item.replicate_id))
