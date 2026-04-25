"""Species-level parallel execution."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
from pathlib import Path
from typing import Any
import warnings

import pandas as pd


SpeciesTask = tuple[str, pd.DataFrame, dict[str, Any]]


def _best_mp_context() -> mp.context.BaseContext:
    available = mp.get_all_start_methods()
    method = "fork" if "fork" in available else available[0]
    return mp.get_context(method)


def _species_task(payload: SpeciesTask) -> tuple[str, Any]:
    species_name, group_df, thin_kwargs = payload
    from pyspthin.api import thin

    normalized_kwargs = dict(thin_kwargs)
    if "out_dir" in normalized_kwargs and normalized_kwargs["out_dir"] is not None:
        normalized_kwargs["out_dir"] = Path(normalized_kwargs["out_dir"])
    if "log_file" in normalized_kwargs and normalized_kwargs["log_file"] is not None:
        normalized_kwargs["log_file"] = Path(normalized_kwargs["log_file"])

    return species_name, thin(group_df, **normalized_kwargs)


def run_species_tasks(tasks: list[SpeciesTask], n_jobs: int) -> dict[str, Any]:
    if n_jobs <= 1 or len(tasks) <= 1:
        return dict(_species_task(task) for task in tasks)

    try:
        with ProcessPoolExecutor(max_workers=n_jobs, mp_context=_best_mp_context()) as executor:
            futures = [executor.submit(_species_task, task) for task in tasks]
            return dict(future.result() for future in futures)
    except Exception as exc:  # pragma: no cover - exercised only on platform-specific failures
        warnings.warn(f"Falling back to threaded species execution because process parallelism failed: {exc}")
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            futures = [executor.submit(_species_task, task) for task in tasks]
            return dict(future.result() for future in futures)

