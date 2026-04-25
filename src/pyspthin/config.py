"""Configuration models for pyspthin."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ParallelMode = Literal["rep", "species"]


class ThinConfig(BaseModel):
    """Validated configuration for single-species thinning runs."""

    model_config = ConfigDict(extra="forbid")

    thin_par: float = Field(gt=0)
    reps: int = Field(gt=0)
    lat_col: str = "LAT"
    long_col: str = "LONG"
    species_col: str = "SPEC"
    record_id_col: str | None = None
    seed: int = Field(default=123, ge=0)
    n_jobs: int = Field(default=1, ge=1)
    write_csv: bool = False
    out_dir: Path | None = None
    out_base: str = "thinned_data"
    max_files: int = Field(default=5, ge=1)
    write_log: bool = False
    log_file: Path | None = None
    max_conflict_edges: int | None = Field(default=None, ge=1)
    earth_radius_km: float = Field(default=6371.0088, gt=0)

    @model_validator(mode="after")
    def set_output_defaults(self) -> ThinConfig:
        if self.write_csv and self.out_dir is None:
            self.out_dir = Path("pyspthin_output")
        if self.write_log and self.log_file is None:
            self.log_file = Path("pyspthin.log")
        return self


class ThinManyConfig(ThinConfig):
    """Validated configuration for multi-species thinning runs."""

    parallel_mode: ParallelMode = "rep"
