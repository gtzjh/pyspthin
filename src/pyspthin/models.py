"""Structured result models for pyspthin."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class ConflictGraphStats(BaseModel):
    """Basic metadata about the sparse conflict graph."""

    model_config = ConfigDict(extra="forbid")

    node_count: int
    edge_count: int
    average_degree: float
    max_degree: int
    estimated_bytes: int


class ReplicateResult(BaseModel):
    """A single thinning replicate."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    replicate_id: int
    replicate_rank: int
    seed: int
    retained_record_ids: list[str]
    retained_count: int
    retained_dataframe: pd.DataFrame
    elapsed_seconds: float


class ThinSummary(BaseModel):
    """Summary statistics for a ThinResult."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    max_retained_count: int
    n_max_replicates: int
    frequency_table: pd.DataFrame


class ThinResult(BaseModel):
    """Structured single-species thinning output."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    species: str
    config: dict[str, Any]
    graph_stats: ConflictGraphStats
    replicates: list[ReplicateResult]
    input_row_count: int
    original_columns: list[str]
    record_id_col: str
    started_at: datetime
    ended_at: datetime
    elapsed_seconds: float
    csv_paths: list[Path] = Field(default_factory=list)
    log_path: Path | None = None
    warnings: list[str] = Field(default_factory=list)

    @property
    def best_replicate(self) -> ReplicateResult:
        return self.replicates[0]

    @property
    def best_dataframe(self) -> pd.DataFrame:
        return self.best_replicate.retained_dataframe

    @property
    def retained_counts(self) -> list[int]:
        return [rep.retained_count for rep in self.replicates]


class ThinManyResult(BaseModel):
    """Structured multi-species thinning output."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    config: dict[str, Any]
    species_results: dict[str, ThinResult]
    started_at: datetime
    ended_at: datetime
    elapsed_seconds: float

    @property
    def species_names(self) -> list[str]:
        return list(self.species_results)
