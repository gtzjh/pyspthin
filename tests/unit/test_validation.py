from __future__ import annotations

import unittest

from pyspthin import thin, thin_many

from tests.test_support import load_fixture


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.single = load_fixture("single_species.csv")
        self.multi = load_fixture("multi_species.csv")

    def test_invalid_latitude_raises(self) -> None:
        bad = self.single.copy()
        bad.loc[0, "LAT"] = 95.0

        with self.assertRaises(ValueError):
            thin(bad, thin_par=8.0, reps=2)

    def test_missing_required_column_raises(self) -> None:
        bad = self.single.drop(columns=["LONG"])

        with self.assertRaises(ValueError):
            thin(bad, thin_par=8.0, reps=2)

    def test_duplicate_explicit_record_id_raises(self) -> None:
        bad = self.single.copy()
        bad.loc[1, "OBS_ID"] = bad.loc[0, "OBS_ID"]

        with self.assertRaises(ValueError):
            thin(bad, thin_par=8.0, reps=2, record_id_col="OBS_ID")

    def test_multiple_species_are_rejected_by_thin(self) -> None:
        with self.assertRaises(ValueError):
            thin(self.multi, thin_par=8.0, reps=2)

    def test_invalid_parallel_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            thin_many(self.multi, thin_par=8.0, reps=2, parallel_mode="auto")


if __name__ == "__main__":
    unittest.main()

