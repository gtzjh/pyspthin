"""Input validation helpers for pyspthin."""

from __future__ import annotations

from dataclasses import dataclass
import warnings
from typing import Any

import pandas as pd

from pyspthin.config import ThinConfig


@dataclass(slots=True)
class ValidatedData:
    """Normalized tabular input ready for graph construction."""

    dataframe: pd.DataFrame
    original_columns: list[str]
    species_name: str | None
    lat_col: str
    long_col: str
    species_col: str
    record_id_col: str
    warnings: list[str]


def _coerce_dataframe(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy(deep=True)
    return pd.DataFrame(data)


def _apply_missing_policy(df: pd.DataFrame, required_cols: list[str], missing_policy: str) -> tuple[pd.DataFrame, list[str]]:
    warnings_list: list[str] = []
    missing_mask = df[required_cols].isna().any(axis=1)
    if not bool(missing_mask.any()):
        return df, warnings_list

    if missing_policy == "error":
        raise ValueError("Required columns contain missing values.")

    dropped = int(missing_mask.sum())
    warnings_list.append(f"Dropped {dropped} row(s) with missing required values.")
    warnings.warn(warnings_list[-1], stacklevel=2)
    return df.loc[~missing_mask].copy(), warnings_list


def _prepare_base_dataframe(data: Any, config: ThinConfig) -> tuple[pd.DataFrame, list[str], list[str]]:
    df = _coerce_dataframe(data)
    if df.empty:
        raise ValueError("Input data is empty.")

    original_columns = list(df.columns)
    required_cols = [config.long_col, config.lat_col, config.species_col]
    if config.record_id_col is not None:
        required_cols.append(config.record_id_col)

    missing_cols = [column for column in required_cols if column not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}")

    df[config.long_col] = pd.to_numeric(df[config.long_col], errors="coerce")
    df[config.lat_col] = pd.to_numeric(df[config.lat_col], errors="coerce")

    df, warning_messages = _apply_missing_policy(df, required_cols, config.missing_policy)
    if df.empty:
        raise ValueError("No rows remain after applying the missing-value policy.")

    if not df[config.long_col].between(-180.0, 180.0).all():
        raise ValueError("Longitude values must lie within [-180, 180].")
    if not df[config.lat_col].between(-90.0, 90.0).all():
        raise ValueError("Latitude values must lie within [-90, 90].")

    df[config.species_col] = df[config.species_col].astype(str)
    return df.reset_index(drop=True), original_columns, warning_messages


def _attach_record_id(df: pd.DataFrame, config: ThinConfig) -> tuple[pd.DataFrame, str]:
    if config.record_id_col is not None:
        record_ids = df[config.record_id_col].astype(str)
    else:
        candidate_column = next(
            (
                column
                for column in ("record_id", "OBS_ID", "obs_id", "ID", "id")
                if column in df.columns and not df[column].isna().any() and not df[column].astype(str).duplicated().any()
            ),
            None,
        )
        if candidate_column is not None:
            record_ids = df[candidate_column].astype(str)
        else:
            record_ids = pd.Series(
                [f"record-{index:06d}" for index in range(len(df))],
                index=df.index,
                dtype="string",
            )

    if record_ids.isna().any():
        raise ValueError("record_id values may not be missing.")
    if record_ids.duplicated().any():
        raise ValueError("record_id values must be unique.")

    df = df.copy()
    df["record_id"] = record_ids.astype(str)
    return df, "record_id"


def validate_single_species_data(data: Any, config: ThinConfig) -> ValidatedData:
    df, original_columns, warnings_list = _prepare_base_dataframe(data, config)
    unique_species = pd.unique(df[config.species_col])
    if len(unique_species) != 1:
        raise ValueError("thin(...) accepts exactly one species. Use thin_many(...) for multi-species data.")

    df, record_id_col = _attach_record_id(df, config)
    return ValidatedData(
        dataframe=df,
        original_columns=original_columns,
        species_name=str(unique_species[0]),
        lat_col=config.lat_col,
        long_col=config.long_col,
        species_col=config.species_col,
        record_id_col=record_id_col,
        warnings=warnings_list,
    )


def validate_multi_species_data(data: Any, config: ThinConfig) -> ValidatedData:
    df, original_columns, warnings_list = _prepare_base_dataframe(data, config)
    df, record_id_col = _attach_record_id(df, config)
    return ValidatedData(
        dataframe=df,
        original_columns=original_columns,
        species_name=None,
        lat_col=config.lat_col,
        long_col=config.long_col,
        species_col=config.species_col,
        record_id_col=record_id_col,
        warnings=warnings_list,
    )
