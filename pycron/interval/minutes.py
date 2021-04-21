from datetime import timedelta
from typing import Dict

from pycron.interval.interval import Interval


class Minutes(Interval):

    def _at(self, at: str) -> Dict:
        return {}

    def time_delta(self) -> timedelta:
        return timedelta(minutes=self.every)
