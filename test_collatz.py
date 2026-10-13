import unittest

from collatz import collatz_sequence, collatz_step, longest_chain, stopping_time


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


if __name__ == "__main__":
    unittest.main()
