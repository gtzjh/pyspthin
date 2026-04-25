"""Restore retained rows from retained record identifiers or indices."""

from __future__ import annotations

import pandas as pd


def restore_replicate_dataframe(
    dataframe: pd.DataFrame,
    retained_indices: list[int],
    replicate_id: int,
    replicate_rank: int,
    species_col: str,
) -> pd.DataFrame:
    restored = dataframe.iloc[retained_indices].copy().reset_index(drop=True)
    retained_count = len(restored)
    species_value = restored[species_col].iloc[0] if retained_count else None
    restored["replicate_id"] = replicate_id
    restored["replicate_rank"] = replicate_rank
    restored["retained_count"] = retained_count
    restored["species"] = species_value
    return restored

