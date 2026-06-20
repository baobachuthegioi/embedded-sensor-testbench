import tempfile
import unittest
from pathlib import Path

from testbench.analysis import detect_outliers, moving_average, read_samples, summarize, validate_run
from testbench.simulate import generate_samples, write_csv


class AnalysisTests(unittest.TestCase):
    def test_moving_average_uses_available_prefix(self):
        self.assertEqual(moving_average([10, 20, 30], window=2), [10, 15, 25])

    def test_simulated_run_passes_default_validation(self):
        rows = generate_samples(samples=120, seed=7)

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "run.csv"
            write_csv(rows, csv_path)
            samples = read_samples(csv_path)

        result = validate_run(samples)

        self.assertTrue(result["passed"])
        self.assertEqual(result["outlier_count"], 0)

    def test_summary_reports_duration_and_voltage_range(self):
        rows = generate_samples(samples=10, interval_ms=20, seed=3)

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "run.csv"
            write_csv(rows, csv_path)
            samples = read_samples(csv_path)

        summary = summarize(samples)

        self.assertEqual(summary["sample_count"], 10)
        self.assertEqual(summary["duration_ms"], 180)
        self.assertGreater(summary["voltage_max_mv"], summary["voltage_min_mv"])

    def test_detect_outliers_flags_large_spike(self):
        rows = generate_samples(samples=80, seed=11)
        rows[40]["voltage_mv"] = 4800.0
        rows[40]["raw_adc"] = 982

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "run.csv"
            write_csv(rows, csv_path)
            samples = read_samples(csv_path)

        outliers = detect_outliers(samples, threshold_mv=500.0)

        self.assertEqual(len(outliers), 1)
        self.assertEqual(outliers[0].sample_id, 40)


if __name__ == "__main__":
    unittest.main()
