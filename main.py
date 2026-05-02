"""Minimal runnable example for pyspthin."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

from pyspthin import plot_thin, summary_thin, thin, thin_many

matplotlib.use("Agg")



def main() -> None:
    data = pd.read_csv("tests/test_data/test2_points.csv", encoding="utf-8")
    print(data)

    # single_species = data.loc[data["SPEC"] == "sp1"].reset_index(drop=True)
    # single_result = thin(single_species, thin_par=8.0, reps=4, seed=123)
    # single_summary = summary_thin(single_result)

    # print("Single-species run")
    # print(single_summary)
    # print(single_result.best_dataframe.to_string(index=False))

    # figure = plot_thin(single_result)
    # output_plot = Path("main_example_plot.png")
    # figure.savefig(output_plot)
    # print(f"Saved diagnostic plot to {output_plot}")

    multi_result = thin_many(
        data,
        thin_par=8.0,
        reps=3,
        seed=999,
        n_jobs=1,
        parallel_mode="species",
    )

    print("\nMulti-species run")
    for species, result in multi_result.species_results.items():
        print(f"{species}: {[rep.retained_count for rep in result.replicates]}")


if __name__ == "__main__":
    main()
