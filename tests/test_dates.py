"""Tests for week/month detection logic.

Run with: python3 -m unittest discover tests
"""

import importlib
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from journal import config

# journal.commands re-exports month_review as the run() function, so import the
# module itself rather than the shadowing attribute
month_review = importlib.import_module("journal.commands.month_review")


class TestWeekOwner(unittest.TestCase):
    def test_week_fully_inside_one_month(self):
        # Sun Aug 9 - Sat Aug 15, 2026
        self.assertEqual(config.week_owner(date(2026, 8, 12)), (2026, 8))

    def test_week_mostly_in_previous_month(self):
        # Sun Jul 26 - Sat Aug 1, 2026: 6 July days, 1 August day
        self.assertEqual(config.week_owner(date(2026, 8, 1)), (2026, 7))

    def test_week_mostly_in_next_month(self):
        # Sun Aug 30 - Sat Sep 5, 2026: 2 August days, 5 September days
        self.assertEqual(config.week_owner(date(2026, 8, 31)), (2026, 9))

    def test_week_spanning_year_boundary(self):
        # Sun Dec 27 2026 - Sat Jan 2 2027: 5 December days, 2 January days
        self.assertEqual(config.week_owner(date(2027, 1, 1)), (2026, 12))

    def test_every_day_of_a_week_agrees(self):
        owners = {config.week_owner(date(2026, 7, day)) for day in range(26, 32)}
        self.assertEqual(owners, {(2026, 7)})


class TestLastWeekEndOfMonth(unittest.TestCase):
    def test_month_owns_the_week_containing_its_last_day(self):
        # July 2026 ends Fri Jul 31, in the week Jul 26 - Aug 1, which July owns
        self.assertEqual(config.last_week_end_of_month(2026, 7), date(2026, 8, 1))

    def test_month_does_not_own_the_week_containing_its_last_day(self):
        # August 2026 ends Mon Aug 31, in the week Aug 30 - Sep 5, owned by
        # September, so August's last week is the one ending Aug 29
        self.assertEqual(config.last_week_end_of_month(2026, 8), date(2026, 8, 29))

    def test_year_boundary(self):
        # December 2026 ends Thu Dec 31, in the week Dec 27 - Jan 2, owned by December
        self.assertEqual(config.last_week_end_of_month(2026, 12), date(2027, 1, 2))


class TestDetectReviewMonth(unittest.TestCase):
    def assert_month(self, today, expected):
        self.assertEqual(
            config.detect_review_month(today), date(*expected, 1), f"on {today}"
        )

    def test_first_of_month_targets_previous_month(self):
        # The complaint: never review August on Aug 1
        self.assert_month(date(2026, 8, 1), (2026, 7))

    def test_mid_month_still_targets_previous_month(self):
        self.assert_month(date(2026, 8, 10), (2026, 7))

    def test_flips_when_the_month_last_week_closes(self):
        self.assert_month(date(2026, 8, 28), (2026, 7))
        self.assert_month(date(2026, 8, 29), (2026, 8))

    def test_stays_put_into_the_next_month(self):
        self.assert_month(date(2026, 8, 30), (2026, 8))
        self.assert_month(date(2026, 9, 5), (2026, 8))

    def test_year_rollover(self):
        # December 2026's last week ends Sat Jan 2 2027
        self.assert_month(date(2027, 1, 1), (2026, 11))
        self.assert_month(date(2027, 1, 2), (2026, 12))

    def test_never_targets_an_unfinished_month(self):
        d = date(2026, 1, 1)
        while d < date(2029, 1, 1):
            target = config.detect_review_month(d)
            closed = config.last_week_end_of_month(target.year, target.month)
            self.assertLessEqual(closed, d, f"on {d}")
            d = date.fromordinal(d.toordinal() + 1)


class TestBoundaryWeeksCountOnce(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        original = config.JOURNAL_DIR
        config.JOURNAL_DIR = Path(self._tmp.name)
        self.addCleanup(lambda: setattr(config, "JOURNAL_DIR", original))

    def write_review(self, saturday):
        path = config.review_path(saturday)
        config.ensure_dir(path)
        path.write_text("# Weekly Review\n")

    def test_straddling_week_belongs_to_exactly_one_month(self):
        # Sat Aug 1 2026 closes a week with 6 July days
        self.write_review(date(2026, 8, 1))

        july = month_review.find_weekly_reviews_for_month(date(2026, 7, 15))
        august = month_review.find_weekly_reviews_for_month(date(2026, 8, 15))

        self.assertEqual([sunday for sunday, _ in july], [date(2026, 7, 26)])
        self.assertEqual(august, [])

    def test_consistency_counts_do_not_double_count(self):
        for saturday in [date(2026, 8, 1), date(2026, 8, 8), date(2026, 8, 15)]:
            self.write_review(saturday)

        self.assertEqual(
            month_review.calculate_consistency(date(2026, 7, 15))["weekly_reviews"], 1
        )
        self.assertEqual(
            month_review.calculate_consistency(date(2026, 8, 15))["weekly_reviews"], 2
        )


if __name__ == "__main__":
    unittest.main()
