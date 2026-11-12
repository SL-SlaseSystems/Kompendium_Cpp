"""Test kontraktu procesu: wynik, diagnostyka i kody wyjścia."""
import subprocess
import sys
import unittest

PROGRAM = sys.argv.pop(1)


class StatsCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([PROGRAM, *args], capture_output=True, text=True, timeout=5)

    def test_valid_values(self):
        result = self.run_cli("10", "-3", "0")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "count=3 sum=7 min=-3 max=10\n")
        self.assertEqual(result.stderr, "")

    def test_one_value(self):
        result = self.run_cli("-9")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "count=1 sum=-9 min=-9 max=-9\n")

    def test_sum_is_wider_than_int(self):
        # 30000 mieści się nawet w minimalnym standardowym int.
        result = self.run_cli(*(["30000"] * 100))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "count=100 sum=3000000 min=30000 max=30000\n")

    def test_no_arguments(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("usage:", result.stderr)

    def test_rejects_invalid_without_partial_result(self):
        for bad in ["", "12x", "+2", " 4", "8 ", "9" * 100]:
            with self.subTest(bad=bad):
                result = self.run_cli("1", bad, "2")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("argument 2", result.stderr)


if __name__ == "__main__":
    unittest.main()
