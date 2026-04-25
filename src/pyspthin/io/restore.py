"""Restore retained rows from retained record identifiers or indices."""

from __future__ import annotations

import pandas as pd

from pyspthin.columns import (
    PYSPTHIN_REPLICATE_ID_COL,
    PYSPTHIN_REPLICATE_RANK_COL,
    PYSPTHIN_RETAINED_COUNT_COL,
    PYSPTHIN_SPECIES_COL,
)


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
    restored[PYSPTHIN_REPLICATE_ID_COL] = replicate_id
    restored[PYSPTHIN_REPLICATE_RANK_COL] = replicate_rank
    restored[PYSPTHIN_RETAINED_COUNT_COL] = retained_count
    restored[PYSPTHIN_SPECIES_COL] = species_value
    return restored
