import unittest

import json
import os
import subprocess
import sys
import tempfile

from collatz import collatz_sequence, collatz_step, longest_chain, plot_html, stopping_time


class CollatzTest(unittest.TestCase):
    def test_step(self):
        self.assertEqual(collatz_step(6), 3)
        self.assertEqual(collatz_step(3), 10)

    def test_sequence(self):
        self.assertEqual(collatz_sequence(1), [1])
        self.assertEqual(collatz_sequence(6), [6, 3, 10, 5, 16, 8, 4, 2, 1])

    def test_stopping_time(self):
        self.assertEqual(stopping_time(1), 0)
        self.assertEqual(stopping_time(27), 111)
        self.assertEqual(stopping_time(27), len(collatz_sequence(27)) - 1)

    def test_longest_chain(self):
        self.assertEqual(longest_chain(10), (9, 19))
        self.assertEqual(longest_chain(1_000_000), (837799, 524))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            collatz_sequence(0)
        with self.assertRaises(ValueError):
            stopping_time(-5)
        with self.assertRaises(ValueError):
            plot_html(0)

    def test_plot_html(self):
        html = plot_html(13)
        self.assertIn("<title>Collatz Sequence 13</title>", html)
        self.assertIn(f"const seq = {json.dumps(collatz_sequence(13))};", html)
        self.assertNotIn("__START__", html)
        self.assertNotIn("__SEQ__", html)

    def test_plot_cli(self):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "collatz.py")
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, script, "13", "--plot"],
                                    cwd=tmp, capture_output=True, text=True, check=True)
            self.assertIn("collatz-13.html", result.stdout)
            with open(os.path.join(tmp, "collatz-13.html"), encoding="utf-8") as f:
                self.assertEqual(f.read(), plot_html(13))

            custom = os.path.join(tmp, "graph.html")
            subprocess.run([sys.executable, script, "13", "--plot", custom], check=True,
                           capture_output=True)
            self.assertTrue(os.path.exists(custom))

            missing_n = subprocess.run([sys.executable, script, "--plot"],
                                       capture_output=True, text=True)
            self.assertNotEqual(missing_n.returncode, 0)
            self.assertIn("--plot needs a starting value", missing_n.stderr)


if __name__ == "__main__":
    unittest.main()
