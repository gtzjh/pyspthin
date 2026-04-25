from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from pyspthin import summary_thin, thin
from tests.test_support import ROOT, load_fixture, load_reference


class RReferenceRegressionTests(unittest.TestCase):
    def test_python_matches_reference_summary(self) -> None:
        data = load_fixture("single_species.csv")
        reference = load_reference("reference_single_species.json")

        if shutil.which("Rscript") is not None:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = Path(tmpdir) / "reference.json"
                subprocess.run(
                    [
                        "Rscript",
                        str(ROOT / "spThin-R" / "scripts" / "run_r_reference.R"),
                        str(ROOT / "tests" / "fixtures" / "single_species.csv"),
                        str(output_path),
                        "8.0",
                        "4",
                        "LONG",
                        "LAT",
                        "123",
                    ],
                    check=True,
                )
                reference = json.loads(output_path.read_text())

        result = thin(data, thin_par=8.0, reps=4, seed=123)
        summary = summary_thin(result)

        self.assertEqual(
            [rep.retained_count for rep in result.replicates], reference["retained_counts"]
        )
        self.assertEqual(summary.max_retained_count, reference["max_retained_count"])
        self.assertEqual(summary.n_max_replicates, reference["n_max_replicates"])


if __name__ == "__main__":
    unittest.main()
