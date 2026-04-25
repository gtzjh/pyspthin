"""Top-level API for pyspthin."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

import pandas as pd

from pyspthin.algorithm.runner import ReplicateExecution, sort_executions
from pyspthin.config import ThinConfig, ThinManyConfig
from pyspthin.graph.conflict_graph import build_conflict_graph
from pyspthin.io.csv_writer import write_best_replicates_to_csv
from pyspthin.io.restore import restore_replicate_dataframe
from pyspthin.logging import write_log
from pyspthin.models import ReplicateResult, ThinManyResult, ThinResult
from pyspthin.parallel.random_state import derive_child_seeds
from pyspthin.parallel.rep import run_replicates
from pyspthin.parallel.species import SpeciesTask, run_species_tasks
from pyspthin.plotting.plot import plot_result
from pyspthin.plotting.summary import summarize_result
from pyspthin.validate import ValidatedData, validate_multi_species_data, validate_single_species_data


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_species_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "species"


def _build_replicate_results(
    validated: ValidatedData,
    executions: list[ReplicateExecution],
) -> list[ReplicateResult]:
    replicate_results: list[ReplicateResult] = []
    for rank, execution in enumerate(sort_executions(executions), start=1):
        restored = restore_replicate_dataframe(
            validated.dataframe,
            execution.retained_indices,
            execution.replicate_id,
            rank,
            validated.species_col,
        )
        replicate_results.append(
            ReplicateResult(
                replicate_id=execution.replicate_id,
                replicate_rank=rank,
                seed=execution.seed,
                retained_record_ids=restored["record_id"].astype(str).tolist(),
                retained_count=execution.retained_count,
                retained_dataframe=restored,
                elapsed_seconds=execution.elapsed_seconds,
            )
        )
    return replicate_results


def _thin_impl(validated: ValidatedData, config: ThinConfig) -> ThinResult:
    started_at = _now()
    graph = build_conflict_graph(
        validated.dataframe,
        long_col=validated.long_col,
        lat_col=validated.lat_col,
        thin_par_km=config.thin_par,
        earth_radius_km=config.earth_radius_km,
        max_conflict_edges=config.max_conflict_edges,
    )

    seeds = derive_child_seeds(config.seed, config.reps, namespace=(graph.node_count, graph.edge_count))
    executions = run_replicates(graph, seeds, config.n_jobs)
    replicate_results = _build_replicate_results(validated, executions)
    ended_at = _now()

    result = ThinResult(
        species=validated.species_name or "unknown",
        config=config.model_dump(mode="python"),
        graph_stats=graph.stats(),
        replicates=replicate_results,
        input_row_count=len(validated.dataframe),
        original_columns=validated.original_columns,
        record_id_col=validated.record_id_col,
        started_at=started_at,
        ended_at=ended_at,
        elapsed_seconds=(ended_at - started_at).total_seconds(),
        warnings=validated.warnings,
    )

    if config.write_csv and config.out_dir is not None:
        result.csv_paths = write_best_replicates_to_csv(
            result,
            out_dir=Path(config.out_dir),
            out_base=config.out_base,
            max_files=config.max_files,
        )

    if config.write_log and config.log_file is not None:
        result.log_path = write_log(Path(config.log_file), result)

    return result


def thin(data: Any, **kwargs: Any) -> ThinResult:
    config = ThinConfig(**kwargs)
    validated = validate_single_species_data(data, config)
    return _thin_impl(validated, config)


def thin_many(data: Any, **kwargs: Any) -> ThinManyResult:
    config = ThinManyConfig(**kwargs)
    validated = validate_multi_species_data(data, config)
    started_at = _now()
    grouped = list(validated.dataframe.groupby(validated.species_col, sort=False))
    species_seeds = derive_child_seeds(config.seed, len(grouped), namespace=(len(grouped),))

    species_results: dict[str, ThinResult]
    if config.parallel_mode == "species":
        tasks: list[SpeciesTask] = []
        for index, (species_name, group_df) in enumerate(grouped):
            child_kwargs = config.model_dump(mode="python")
            child_kwargs.pop("parallel_mode", None)
            child_kwargs["seed"] = species_seeds[index]
            child_kwargs["n_jobs"] = 1
            child_kwargs["record_id_col"] = "record_id"
            if config.write_csv and config.out_dir is not None:
                child_kwargs["out_dir"] = Path(config.out_dir) / _safe_species_name(str(species_name))
            if config.write_log and config.log_file is not None:
                log_path = Path(config.log_file)
                child_kwargs["log_file"] = log_path.with_name(
                    f"{log_path.stem}_{_safe_species_name(str(species_name))}{log_path.suffix or '.log'}"
                )
            tasks.append((str(species_name), group_df.reset_index(drop=True), child_kwargs))
        species_results = run_species_tasks(tasks, config.n_jobs)
    else:
        species_results = {}
        for index, (species_name, group_df) in enumerate(grouped):
            child_kwargs = config.model_dump(mode="python")
            child_kwargs.pop("parallel_mode", None)
            child_kwargs["seed"] = species_seeds[index]
            child_kwargs["record_id_col"] = "record_id"
            if config.write_csv and config.out_dir is not None:
                child_kwargs["out_dir"] = Path(config.out_dir) / _safe_species_name(str(species_name))
            if config.write_log and config.log_file is not None:
                log_path = Path(config.log_file)
                child_kwargs["log_file"] = log_path.with_name(
                    f"{log_path.stem}_{_safe_species_name(str(species_name))}{log_path.suffix or '.log'}"
                )
            species_results[str(species_name)] = thin(group_df.reset_index(drop=True), **child_kwargs)

    ended_at = _now()
    return ThinManyResult(
        config=config.model_dump(mode="python"),
        species_results=species_results,
        started_at=started_at,
        ended_at=ended_at,
        elapsed_seconds=(ended_at - started_at).total_seconds(),
    )


def summary_thin(result: ThinResult, show: bool = False):
    return summarize_result(result, show=show)


def plot_thin(result: ThinResult, which: tuple[int, ...] = (1, 2, 3), **kwargs: Any):
    return plot_result(result, which=which, **kwargs)
