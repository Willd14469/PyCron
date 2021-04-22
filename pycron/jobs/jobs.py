import re
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from uuid import uuid4

from pycron.interval.days import Days
from pycron.interval.hours import Hours
from pycron.interval.interval import Interval
from pycron.interval.minutes import Minutes
from pycron.interval.weeks import Weeks
from pycron.settings import RELATIVE_JOB_FOLDER, JOB_FAIL_TIMEOUT_PERIOD_MINUTES


class InvalidJobException(Exception):
    ...


class JobRunReasons(Enum):
    JOB_FAILED = 'Job failed rerun'
    ROUTINE = 'Scheduled run'


class Job:
    """
    Each script in the job_folder is created as a Job.

    The relative path of the script gets parsed to compute the interval the job will be run according to.

    Provides interfaces for:

        next_execution  ->  When the job next needs to run
        success         ->  Signals that the job was run correctly and that the next execution is according to the interval
        fail            ->  Signals that the job was not run correctly and that the next execution is a re-run rather
                            than a scheduled run. This re-run will be according to JOB_FAIL_TIMEOUT_PERIOD_MINUTES

    Acceptable every folders:
        min     -> runs every x minutes
        hour    -> runs every x hours
        day     -> runs every x days
        week    -> runs every x weeks

    Acceptable at folders:
        min     -> no at parameters
        hour    |
                |-> at00<xx> for running at xx minutes every hour
        day     |
                |-> at<yy><xx> for running on yy hour at xx minutes
        week    |
                |-> at<yy><xx> for running on yy hour at xx minutes every week

    Example:
        jobs_root
            |-> 1min
                    |-> run_every_min.sh
            |-> 1hour
                    |-> at0050
                            |-> run_every_hour_at_10_to.sh
                    |-> at0030
                            |-> run_every_hour_at_half_past.sh
                    |-> run_every_hour_on_the_hour.sh
            |-> 1week
                    |-> at0015
                            |-> run_weekly_at_quarter_past.sh


    """

    def __init__(self, script_path: Path):
        # Absolute path to script
        self.script_path = script_path
        # Truncated path relative to job folder
        self.relative_name = script_path.relative_to(RELATIVE_JOB_FOLDER)

        self.job_uuid = uuid4()

        # Interval for the job to be run
        self.interval: Interval = None

        # Stores the last successful time the job ran
        self.last_execution = datetime.now()

        #  Stores the last failed time this job ran
        self.last_failed_execution = None

        # Parse the relative name and assign the correct interval
        self._parse_script_folder_structure()

        # Reason the job is going to run
        self.run_reason: JobRunReasons = JobRunReasons.ROUTINE

        # Number of times the job has failed in a row
        self.failed_attempts = 0

        # Signal that the job is currently targeted by a thread for running. Release on completion.
        self.locked = False
        self.locked_at = None
        self.unlocked_at = None

    @property
    def next_execution(self) -> datetime:
        """
        Returns the next datetime the function needs to be executed.

        Takes into account the offset if a job incorrectly runs.
        :return: datetime
        """
        if self.failed_attempts > 0:
            return self.last_failed_execution + timedelta(minutes=JOB_FAIL_TIMEOUT_PERIOD_MINUTES)

        return self.interval.next_time(self.last_execution)

    def _parse_script_folder_structure(self):
        """
        Calculates the required interval based on the relative path of the job
        """

        parent_parts = self.relative_name.parent.parts

        # invalidate scripts in root folder
        if not parent_parts:
            raise InvalidJobException(self.script_path,
                                      f'Script is in the root scripts folder with no definition of how often to run.')

        # Calculate the every part of the interval
        every_parameter = parent_parts[0]
        self.interval = self._parse_every_parameter(every_parameter)

        # Calculate the at part of the interval
        if len(parent_parts) == 2:
            at_parameter = parent_parts[1]

            self._parse_at_parameter(at_parameter)

    def _parse_every_parameter(self, every_parameter: str) -> Interval:
        """
        Calculates the every_parameter of the interval.

        JobFolder
            |-> 1hour
                    |-> at0030
                            |-> helloworld.sh

        The above structure would produce an interval of every 1 hour at half past

        """
        valid_every_parameter_map = {
            'min': Minutes,
            'hour': Hours,
            'day': Days,
            'week': Weeks
        }
        every_parameter_string = '|'.join(valid_every_parameter_map.keys())

        #                    captures every               captures timeinterval      ensures string ends
        regex_match = rf'(?P<every>[0-9]+)(?P<time_interval>{every_parameter_string})\Z'

        matches = re.match(regex_match, every_parameter)

        if not matches:
            raise InvalidJobException(self.script_path,
                                      f'Unable to correctly parse the `every` parameter ({every_parameter}) of the folder structure')

        every = int(matches.group('every'))
        time_interval = matches.group('time_interval')

        interval_obj = valid_every_parameter_map[time_interval](every)

        return interval_obj

    def _parse_at_parameter(self, at_parameter: str):
        """
        Calculates the at_parameter of the interval.

        JobFolder
            |-> 1hour
                    |-> at0030
                            |-> helloworld.sh

        The above structure would produce an interval of every 1 hour at half past

        """
        regex_match = rf'at(?P<at>[0-2][0-3][0-5][0-9])\Z'

        matches = re.match(regex_match, at_parameter)

        if not matches:
            raise InvalidJobException(self.script_path,
                                      f'Unable to correctly parse the `at` parameter ({at_parameter}) of the folder structure')

        at_str = matches['at']

        self.interval.at(at_str)

    def success(self):
        """
        Job ran successfully - Set it up for the next scheduled run

        Provides a hook for subclasses to implement the correct running acknowledgement

        Sets the last_execution to current datetime
        Sets failed_attempts to 0
        Sets run_reason the routine scheduled reason
        """
        self.last_execution = datetime.now()
        self.failed_attempts = 0
        self.run_reason = JobRunReasons.ROUTINE
        self.unlock()

    def fail(self):
        """
        Job did not run successfully - Sets up the job to run after a timeout period

        Provides a hook for subclasses to implement the incorrect running acknowledgement

        Increments the failed_attempts by 1
        Sets run_reason to indicate the job failed to run successfully
        """
        self.failed_attempts += 1
        self.last_failed_execution = datetime.now()
        self.run_reason = JobRunReasons.JOB_FAILED
        self.unlock()

    def lock(self):
        """
        Signal that the job is targeted by a thread and not to spawn a new thread to run it.

        This should be called by the executor
        """
        self.locked = True
        self.locked_at = datetime.now()

    def unlock(self):
        """
        Release lock signaling the job is runnable again.

        Handled by this object on the completion methods
        :return:
        """
        self.locked = False
        self.unlocked_at = datetime.now()

    @property
    def runtime(self):
        assert not self.locked, 'Cannot calculate runtime while job is running'

        runtime:timedelta = self.unlocked_at - self.locked_at

        secs = runtime.seconds

        return f'{secs // 3600} hours, {secs // 60} minutes, {secs % 60} seconds'


    def __str__(self):
        return str(self.relative_name)

    def __repr__(self):
        return self.__str__()


test = Job(Path(r'C:\Coding\miniprojects\pycron\testing\1hour\at0050\test.bat'))
