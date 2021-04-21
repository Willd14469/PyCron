import abc
from datetime import datetime, timedelta
from typing import Dict


class Interval(abc.ABC):
    """
    Root class for job intervals

    Children need to implement the Time_delta function to generate the correct datetime.timedelta object for the next_time method
    """
    at_data = {}  # Parameters passed to datetime.replace function.

    # Used to calculate the number of time units to wait between jobs
    # Implemented by subclasses in the time_delta method
    every = None

    def __init__(self, every, at: str = None):
        self.every = every
        if at is not None:
            self.at_data = self._at(at)
        else:
            self.at_data = {}

    def next_time(self, last_run=None):
        int_at = {k: int(v) for k, v in self.at_data.items()}

        if last_run is None:
            last_run = datetime.now()

        last_run = last_run.replace(second=00, microsecond=00)

        # Try to just set the values and see if this is in the future
        # If this value is in the future then use it
        possible_time = last_run.replace(**int_at)

        if possible_time > last_run:
            return possible_time

        next_datetime = last_run + self.time_delta()

        next_datetime = next_datetime.replace(**int_at)

        return next_datetime

    def planned_schedule(self, n=10):
        """
        Calculate a list of n scheduled runs
        """
        schedule = []
        for i in range(n):
            if not schedule:
                schedule.append(self.next_time())
            else:
                schedule.append(self.next_time(schedule[-1]))
        return schedule

    @abc.abstractmethod
    def _at(self, at: str) -> Dict:
        """
        Used to set the correct parameters in the at property of the class

        This property is then passed to the datetime.replace function as kwargs

        This effectively sets the correct min, hour, and day params.
        """
        ...

    def at(self, at: str):
        self.at_data = self._at(at)

    @abc.abstractmethod
    def time_delta(self) -> timedelta:
        """
        Used to calculate the timedelta for the next possible schedule time

        Boils down to the `run every x` part of a cron job

        This is set by subclasses that implement the length of the interval such as Days,Minutes and Weeks classes

        :return: datetime.timedelta
        """
        ...
