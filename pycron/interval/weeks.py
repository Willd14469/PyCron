from datetime import timedelta
from typing import Dict

from pycron.interval.days import Days
from pycron.interval.interval import Interval


class Weeks(Days):

    def time_delta(self) -> timedelta:
        return timedelta(weeks=self.every)
