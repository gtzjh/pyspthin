"""Memory and density guards for conflict graph creation."""

from __future__ import annotations


def ensure_edge_limit(edge_count: int, max_conflict_edges: int | None) -> None:
    if max_conflict_edges is not None and edge_count > max_conflict_edges:
        raise ValueError(
            "Conflict graph exceeds the configured max_conflict_edges limit. "
            f"edge_count={edge_count}, max_conflict_edges={max_conflict_edges}"
        )


def estimate_adjacency_bytes(adjacency_lengths: list[int], index_size_bytes: int = 4) -> int:
    return sum(length * index_size_bytes for length in adjacency_lengths)

