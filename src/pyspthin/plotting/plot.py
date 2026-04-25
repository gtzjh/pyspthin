"""Diagnostic plotting helpers."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from pyspthin.models import ThinResult


def plot_result(
    result: ThinResult,
    which: Sequence[int] = (1, 2, 3),
    shuffle_seed: int = 0,
    **kwargs: object,
) -> Figure:
    selected = list(which)
    if not selected:
        raise ValueError("At least one plot index must be requested.")

    counts = np.asarray([rep.retained_count for rep in result.replicates], dtype=float)
    shuffled_counts = counts.copy()
    np.random.default_rng(shuffle_seed).shuffle(shuffled_counts)
    cummax_counts = np.maximum.accumulate(shuffled_counts)

    figure, axes = plt.subplots(1, len(selected), figsize=(5 * len(selected), 4))
    if len(selected) == 1:
        axes = [axes]

    for axis, plot_id in zip(axes, selected, strict=True):
        if plot_id == 1:
            axis.plot(np.arange(1, len(cummax_counts) + 1), cummax_counts, **kwargs)
            axis.set_xlabel("Number Repetitions")
            axis.set_ylabel("Cumulative Maximum Records Retained")
        elif plot_id == 2:
            x_values = np.arange(1, len(cummax_counts) + 1, dtype=float)
            axis.plot(np.log(x_values), np.log(cummax_counts), **kwargs)
            axis.set_xlabel("Log Number Repetitions")
            axis.set_ylabel("Log Cumulative Maximum Records Retained")
        elif plot_id == 3:
            axis.hist(shuffled_counts, **kwargs)
            axis.set_xlabel("Maximum Records Retained")
            axis.set_ylabel("Frequency")
        else:
            raise ValueError(f"Unsupported plot index: {plot_id}")

    figure.tight_layout()
    return figure
