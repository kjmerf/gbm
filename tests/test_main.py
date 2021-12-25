from datetime import datetime, timezone
import unittest

from src import main


class TestMain(unittest.TestCase):
    def test_get_dt_from_string(self):
        self.assertEqual(
            main.get_dt_from_string("2021-01-03-05"),
            datetime(2021, 1, 3, 5, tzinfo=timezone.utc),
        )

    def test_get_iterations(self):
        self.assertEqual(
            main.get_iterations(
                datetime(2021, 1, 2, 1, tzinfo=timezone.utc),
                datetime(2021, 1, 1, 0, tzinfo=timezone.utc),
            ),
            25,
        )


if __name__ == "__main__":
    unittest.main()
