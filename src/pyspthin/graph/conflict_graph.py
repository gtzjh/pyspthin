"""Sparse conflict graph construction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from pyspthin.distance.base import (
    EARTH_RADIUS_KM,
    kilometers_to_radians,
    radians_to_chord_length,
    unit_vectors,
)
from pyspthin.distance.haversine import haversine_radians, to_radians
from pyspthin.graph.guards import ensure_edge_limit, estimate_adjacency_bytes
from pyspthin.models import ConflictGraphStats


@dataclass(frozen=True, slots=True)
class ConflictGraph:
    """Sparse adjacency representation of conflicts under the thinning threshold."""

    adjacency: tuple[NDArray[np.int32], ...]
    initial_degrees: NDArray[np.int32]
    node_count: int
    edge_count: int
    thin_par_km: float
    earth_radius_km: float
    estimated_bytes: int

    def stats(self) -> ConflictGraphStats:
        max_degree = int(self.initial_degrees.max()) if self.node_count else 0
        average_degree = float(self.initial_degrees.mean()) if self.node_count else 0.0
        return ConflictGraphStats(
            node_count=self.node_count,
            edge_count=self.edge_count,
            average_degree=average_degree,
            max_degree=max_degree,
            estimated_bytes=self.estimated_bytes,
        )


def build_conflict_graph(
    dataframe: pd.DataFrame,
    long_col: str,
    lat_col: str,
    thin_par_km: float,
    earth_radius_km: float = EARTH_RADIUS_KM,
    max_conflict_edges: int | None = None,
) -> ConflictGraph:
    node_count = len(dataframe)
    if node_count == 0:
        raise ValueError("Cannot build a conflict graph from an empty dataframe.")

    longitudes_deg = dataframe[long_col].to_numpy(dtype=float)
    latitudes_deg = dataframe[lat_col].to_numpy(dtype=float)
    longitudes_rad, latitudes_rad = to_radians(longitudes_deg, latitudes_deg)
    threshold_radians = kilometers_to_radians(thin_par_km, earth_radius_km)
    chord_threshold = radians_to_chord_length(threshold_radians)
    cell_size = max(chord_threshold, 1e-12)
    vectors = unit_vectors(longitudes_rad, latitudes_rad)

    buckets: dict[tuple[int, int, int], list[int]] = {}
    adjacency_lists: list[list[int]] = [[] for _ in range(node_count)]
    edge_count = 0

    for index, vector in enumerate(vectors):
        cell = tuple(np.floor(vector / cell_size).astype(int).tolist())
        candidate_indices: list[int] = []

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    candidate_indices.extend(
                        buckets.get((cell[0] + dx, cell[1] + dy, cell[2] + dz), ())
                    )

        if candidate_indices:
            candidates = np.asarray(candidate_indices, dtype=np.int32)
            angles = haversine_radians(
                longitudes_rad[index],
                latitudes_rad[index],
                longitudes_rad[candidates],
                latitudes_rad[candidates],
            )
            for other in candidates[angles < threshold_radians]:
                other_index = int(other)
                adjacency_lists[index].append(other_index)
                adjacency_lists[other_index].append(index)
                edge_count += 1
                ensure_edge_limit(edge_count, max_conflict_edges)

        buckets.setdefault(cell, []).append(index)

    adjacency = tuple(
        np.asarray(sorted(neighbors), dtype=np.int32) for neighbors in adjacency_lists
    )
    degrees = np.asarray([len(neighbors) for neighbors in adjacency], dtype=np.int32)
    estimated_bytes = estimate_adjacency_bytes([len(neighbors) for neighbors in adjacency])

    return ConflictGraph(
        adjacency=adjacency,
        initial_degrees=degrees,
        node_count=node_count,
        edge_count=edge_count,
        thin_par_km=thin_par_km,
        earth_radius_km=earth_radius_km,
        estimated_bytes=estimated_bytes,
    )
