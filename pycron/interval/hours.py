from datetime import timedelta
from typing import Dict

from pycron.interval.interval import Interval


class Hours(Interval):

    def time_delta(self):
        return timedelta(hours=self.every)

    def _at(self, at: str) -> Dict:
        return {'minute': int(at[-2:])}
