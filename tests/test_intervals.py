import datetime
from unittest import TestCase

from pycron.interval.days import Days
from pycron.interval.hours import Hours
from pycron.interval.minutes import Minutes
from pycron.interval.weeks import Weeks


class TestInterval(TestCase):
    def test_minutes(self):
        minute_obj = Minutes(2)

        now = datetime.datetime.now()

        next_run = minute_obj.next_time(now)

        next_expected_run = (now + datetime.timedelta(minutes=2)).replace(second=00, microsecond=00)

        self.assertEqual(next_run, next_expected_run)

    def test_hours(self):
        minute_obj = Hours(2)

        now = datetime.datetime.now()

        next_run = minute_obj.next_time(now)

        next_expected_run = (now + datetime.timedelta(hours=2)).replace(second=00, microsecond=00)

        self.assertEqual(next_run, next_expected_run)

    def test_days(self):
        minute_obj = Days(2)

        now = datetime.datetime.now()

        next_run = minute_obj.next_time(now)

        next_expected_run = (now + datetime.timedelta(days=2)).replace(second=00, microsecond=00)

        self.assertEqual(next_run, next_expected_run)

    def test_weeks(self):
        minute_obj = Weeks(2)

        now = datetime.datetime.now()

        next_run = minute_obj.next_time(now)

        next_expected_run = (now + datetime.timedelta(weeks=2)).replace(second=00, microsecond=00)

        self.assertEqual(next_run, next_expected_run)
