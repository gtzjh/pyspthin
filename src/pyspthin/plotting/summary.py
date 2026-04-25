"""Summary helpers for thinning results."""

from __future__ import annotations

import pandas as pd

from pyspthin.models import ThinResult, ThinSummary


def summarize_result(result: ThinResult, show: bool = False) -> ThinSummary:
    counts = [rep.retained_count for rep in result.replicates]
    frequency_table = (
        pd.Series(counts, dtype="int64")
        .value_counts(sort=False)
        .sort_index()
        .rename_axis("retained_count")
        .reset_index(name="frequency")
    )
    summary = ThinSummary(
        max_retained_count=max(counts),
        n_max_replicates=sum(count == max(counts) for count in counts),
        frequency_table=frequency_table,
    )

    if show:
        print(f"Maximum retained count: {summary.max_retained_count}")
        print(f"Number of max replicates: {summary.n_max_replicates}")
        print(summary.frequency_table.to_string(index=False))

    return summary
