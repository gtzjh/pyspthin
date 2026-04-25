"""Greedy thinning logic that mirrors the R package semantics."""

from __future__ import annotations

import numpy as np

from pyspthin.graph.conflict_graph import ConflictGraph


def run_greedy_replicate(graph: ConflictGraph, seed: int) -> list[int]:
    """Run one replicate and return the retained row indices."""

    rng = np.random.default_rng(seed)
    active = np.ones(graph.node_count, dtype=bool)
    degrees = graph.initial_degrees.copy()
    active_count = graph.node_count

    while active_count > 1:
        max_degree = int(degrees.max(initial=0))
        if max_degree <= 0:
            break

        candidates = np.flatnonzero((degrees == max_degree) & active)
        if len(candidates) == 0:
            break

        if len(candidates) == 1:
            remove_index = int(candidates[0])
        else:
            remove_index = int(rng.choice(candidates))

        active[remove_index] = False
        active_count -= 1
        degrees[remove_index] = 0

        for neighbor in graph.adjacency[remove_index]:
            neighbor_index = int(neighbor)
            if active[neighbor_index]:
                degrees[neighbor_index] -= 1

    return [int(index) for index in np.flatnonzero(active)]
