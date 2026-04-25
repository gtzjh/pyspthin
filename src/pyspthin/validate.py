"""Input validation helpers for pyspthin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from pyspthin.columns import PYSPTHIN_RECORD_ID_COL
from pyspthin.config import ThinConfig


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One row-level validation issue."""

    row: object
    field: str
    value: object
    reason: str

    def format(self) -> str:
        return f"row {self.row}, field {self.field}, value {self.value!r}: {self.reason}"


class PyspthinValidationError(ValueError):
    """Validation error with row-level diagnostics."""

    def __init__(self, issues: list[ValidationIssue]) -> None:
        self.issues = issues
        lines = [f"Validation failed with {len(issues)} error(s):"]
        lines.extend(issue.format() for issue in issues)
        super().__init__("\n".join(lines))


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


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    return bool(pd.isna(value))  # type: ignore[call-overload]


def _prepare_base_dataframe(
    data: Any, config: ThinConfig
) -> tuple[pd.DataFrame, list[str], list[str]]:
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

    issues: list[ValidationIssue] = []
    numeric_columns = {
        config.long_col: (pd.to_numeric(df[config.long_col], errors="coerce"), -180.0, 180.0),
        config.lat_col: (pd.to_numeric(df[config.lat_col], errors="coerce"), -90.0, 90.0),
    }

    for column, (coerced_values, minimum, maximum) in numeric_columns.items():
        for row, raw_value, coerced_value in zip(
            df.index,
            df[column],
            coerced_values,
            strict=True,
        ):
            if _is_missing(raw_value):
                issues.append(ValidationIssue(row, column, raw_value, "is missing"))
            elif _is_missing(coerced_value):
                issues.append(ValidationIssue(row, column, raw_value, "must be numeric"))
            elif not minimum <= float(coerced_value) <= maximum:
                issues.append(
                    ValidationIssue(
                        row,
                        column,
                        raw_value,
                        f"must be within [{minimum:g}, {maximum:g}]",
                    )
                )

    for row, raw_value in df[config.species_col].items():
        if _is_missing(raw_value):
            issues.append(ValidationIssue(row, config.species_col, raw_value, "is missing"))
        elif str(raw_value).strip() == "":
            issues.append(ValidationIssue(row, config.species_col, raw_value, "must be non-empty"))

    if issues:
        raise PyspthinValidationError(issues)

    df[config.long_col] = numeric_columns[config.long_col][0].astype(float)
    df[config.lat_col] = numeric_columns[config.lat_col][0].astype(float)

    df[config.species_col] = df[config.species_col].astype(str)
    return df, original_columns, []


def _valid_auto_record_id_source(series: pd.Series) -> bool:
    if series.isna().any():
        return False
    as_strings = series.astype(str)
    if as_strings.str.strip().eq("").any():
        return False
    return not bool(as_strings.duplicated().any())


def _attach_record_id(df: pd.DataFrame, config: ThinConfig) -> tuple[pd.DataFrame, str]:
    if config.record_id_col is not None:
        raw_record_ids = df[config.record_id_col]
        issues: list[ValidationIssue] = []
        for row, raw_value in raw_record_ids.items():
            if _is_missing(raw_value):
                issues.append(ValidationIssue(row, config.record_id_col, raw_value, "is missing"))
            elif str(raw_value).strip() == "":
                issues.append(
                    ValidationIssue(row, config.record_id_col, raw_value, "must be non-empty")
                )

        if not issues:
            record_ids = raw_record_ids.astype(str)
            for row, value in record_ids[record_ids.duplicated()].items():
                issues.append(ValidationIssue(row, config.record_id_col, value, "must be unique"))

        if issues:
            raise PyspthinValidationError(issues)

        record_ids = raw_record_ids.astype(str)
    else:
        candidate_column = next(
            (
                column
                for column in ("OBS_ID", "obs_id", "ID", "id")
                if column in df.columns and _valid_auto_record_id_source(df[column])
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

    df = df.copy()
    df[PYSPTHIN_RECORD_ID_COL] = record_ids.astype(str)
    return df.reset_index(drop=True), PYSPTHIN_RECORD_ID_COL


def validate_single_species_data(data: Any, config: ThinConfig) -> ValidatedData:
    df, original_columns, warnings_list = _prepare_base_dataframe(data, config)
    unique_species = pd.unique(df[config.species_col])
    if len(unique_species) != 1:
        raise ValueError(
            "thin(...) accepts exactly one species. Use thin_many(...) for multi-species data."
        )

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
