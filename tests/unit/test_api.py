from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from pyspthin import plot_thin, summary_thin, thin, thin_many

from tests.test_support import load_fixture


class ThinApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.single = load_fixture("single_species.csv")
        self.ties = load_fixture("single_species_ties.csv")
        self.multi = load_fixture("multi_species.csv")

    def test_thin_preserves_original_columns_and_generates_record_ids(self) -> None:
        result = thin(self.single, thin_par=8.0, reps=4, seed=123)

        self.assertEqual([rep.retained_count for rep in result.replicates], [3, 3, 3, 3])
        retained = result.best_replicate.retained_dataframe
        self.assertEqual(len(retained), 3)
        self.assertTrue(set(self.single.columns).issubset(set(retained.columns)))
        self.assertIn("record_id", retained.columns)
        self.assertEqual(retained["record_id"].nunique(), len(retained))

    def test_summary_and_plot_are_available(self) -> None:
        result = thin(self.single, thin_par=8.0, reps=4, seed=123)
        summary = summary_thin(result)

        self.assertEqual(summary.max_retained_count, 3)
        self.assertEqual(summary.n_max_replicates, 4)
        self.assertEqual(summary.frequency_table.to_dict("records"), [{"retained_count": 3, "frequency": 4}])

        figure = plot_thin(result)
        try:
            self.assertEqual(len(figure.axes), 3)
        finally:
            figure.clf()

    def test_rep_parallel_matches_serial_for_same_seed(self) -> None:
        serial = thin(self.ties, thin_par=8.0, reps=10, seed=77, n_jobs=1)
        parallel = thin(self.ties, thin_par=8.0, reps=10, seed=77, n_jobs=2)

        serial_counts = [rep.retained_count for rep in serial.replicates]
        parallel_counts = [rep.retained_count for rep in parallel.replicates]
        self.assertEqual(serial_counts, parallel_counts)
        self.assertEqual(
            [tuple(rep.retained_record_ids) for rep in serial.replicates],
            [tuple(rep.retained_record_ids) for rep in parallel.replicates],
        )

    def test_thin_many_species_parallel_matches_serial(self) -> None:
        serial = thin_many(self.multi, thin_par=8.0, reps=3, seed=999, n_jobs=1, parallel_mode="species")
        parallel = thin_many(self.multi, thin_par=8.0, reps=3, seed=999, n_jobs=2, parallel_mode="species")

        self.assertEqual(set(serial.species_results), {"sp1", "sp2"})
        self.assertEqual(set(parallel.species_results), {"sp1", "sp2"})
        for species in ["sp1", "sp2"]:
            self.assertEqual(
                [rep.retained_count for rep in serial.species_results[species].replicates],
                [rep.retained_count for rep in parallel.species_results[species].replicates],
            )

    def test_csv_and_log_outputs_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir) / "csv"
            log_file = Path(tmpdir) / "run.log"

            thin(
                self.single,
                thin_par=8.0,
                reps=4,
                seed=321,
                write_csv=True,
                out_dir=out_dir,
                max_files=2,
                write_log=True,
                log_file=log_file,
            )

            csv_files = sorted(out_dir.glob("*.csv"))
            self.assertEqual(len(csv_files), 2)
            self.assertTrue(log_file.exists())
            self.assertIn("Maximum retained count", log_file.read_text())


if __name__ == "__main__":
    unittest.main()

