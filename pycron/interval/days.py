from datetime import timedelta
from typing import Dict

from pycron.interval.interval import Interval


class Days(Interval):

    def _at(self, at: str) -> Dict:
        return {
            'minute': at[-2:],
            'hour': at[:2]
        }

    def time_delta(self) -> timedelta:
        return timedelta(days=self.every)
