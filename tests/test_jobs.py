import datetime
from pathlib import Path
from time import sleep
from unittest import TestCase, expectedFailure

from pycron import SettingsSingleton
from pycron.interval.days import Days
from pycron.interval.hours import Hours
from pycron.interval.minutes import Minutes
from pycron.interval.weeks import Weeks
from pycron.jobs.jobs import Job, JobRunReasons, InvalidJobException


class TestJobs(TestCase):
    def setUp(self) -> None:
        self.settings = SettingsSingleton.get_settings()

        self.job_folder = self.settings.JOBS_FOLDER

        valid_job_path = self.job_folder / '1min/hello.sh'

        self.test_job = Job(valid_job_path)

    def test_success_method(self):
        """
        Test success method
        """

        job = self.test_job
        job.failed_attempts = 99
        job.run_reason = JobRunReasons.JOB_FAILED
        job.lock()
        job.success()

        self.assertAlmostEqual(job.last_execution, datetime.datetime.now(), msg='Last execution was not correct')
        self.assertEqual(job.failed_attempts, 0, msg='Failed attempts was not reset')
        self.assertEqual(job.run_reason, JobRunReasons.ROUTINE, msg='Run reason was not reset')
        self.assertFalse(job.locked, msg='Job was not unlocked')

    def test_fail_method(self):
        """
        Test fail method
        """

        job = self.test_job
        job.failed_attempts = 5
        job.run_reason = JobRunReasons.ROUTINE
        job.lock()
        job.fail()

        self.assertAlmostEqual(job.last_failed_execution, datetime.datetime.now(),
                               msg='Last failed execution was not correct')
        self.assertEqual(job.failed_attempts, 5 + 1, msg='Failed attempts was not reset')
        self.assertEqual(job.run_reason, JobRunReasons.JOB_FAILED, msg='Run reason was not set to `failed` reason')
        self.assertFalse(job.locked, msg='Job was not unlocked')

    def test_locking(self):
        """
        Test the lock and unlock methods
        """

        job = self.test_job

        job.lock()

        self.assertTrue(job.locked)
        self.assertAlmostEqual(job.locked_at, datetime.datetime.now())

        sleep(2)
        job.unlock()

        job_datetime = job.unlocked_at.replace(microsecond=0)
        now = datetime.datetime.now().replace(microsecond=0)

        self.assertFalse(job.locked)
        self.assertEqual(job_datetime, now)

        runtime = job.runtime
        expected_runtime = f'{0} hours, {0} minutes, {2} seconds'
        self.assertEqual(runtime, expected_runtime)

    def test_15min(self):
        path = self.job_folder / '15min/hello.sh'

        job = Job(path)

        self.assertIsInstance(job.interval, Minutes, msg='Type of interval does not match')
        self.assertEqual(job.interval.every, 15, msg='Length of interval does not match')

    def test_1hour(self):
        path = self.job_folder / '1hour/hello.sh'

        job = Job(path)

        self.assertIsInstance(job.interval, Hours, msg='Type of interval does not match')
        self.assertEqual(job.interval.every, 1, msg='Length of interval does not match')
        self.assertEqual({}, job.interval.at_data, msg='')

    def test_1hour45(self):
        path = self.job_folder / '1hour/at0045/hello.sh'

        job = Job(path)

        self.assertIsInstance(job.interval, Hours, msg='Type of interval does not match')
        self.assertEqual(job.interval.every, 1, msg='Length of interval does not match')
        self.assertEqual({'minute': 45}, job.interval.at_data, msg='')

    def test_1dayat1345(self):
        path = self.job_folder / '1day/at1345/hello.sh'

        job = Job(path)

        self.assertIsInstance(job.interval, Days, msg='Type of interval does not match')
        self.assertEqual(job.interval.every, 1, msg='Length of interval does not match')
        self.assertEqual({'hour': '13', 'minute': '45'}, job.interval.at_data, msg='')

    def test_2weekat1733(self):
        path = self.job_folder / '2week/at1733/hello.sh'

        job = Job(path)

        self.assertIsInstance(job.interval, Weeks, msg='Type of interval does not match')
        self.assertEqual(job.interval.every, 2, msg='Length of interval does not match')
        self.assertEqual({'hour': '17', 'minute': '33'}, job.interval.at_data, msg='')

    def test_4weekat2359(self):
        path = self.job_folder / '4week/at2359/hello.sh'

        job = Job(path)

        self.assertIsInstance(job.interval, Weeks, msg='Type of interval does not match')
        self.assertEqual(job.interval.every, 4, msg='Length of interval does not match')
        self.assertEqual({'hour': '23', 'minute': '59'}, job.interval.at_data, msg='')

    def test_invalid_jobs(self):
        invalid_paths = [
            self.job_folder / '2week/at3000/hello.sh',
            self.job_folder / '2week/at0069/hello.sh',
            self.job_folder / 'hello.sh',
            self.job_folder / '2week/at-0988/hello.sh',
            self.job_folder / '2week/at30/hello.sh',
            self.job_folder / '166mins/hello.sh',
            self.job_folder / '2weeks/hello.sh',
            self.job_folder / '2days/hello.sh',
            self.job_folder / '1day',
        ]

        for job_path in invalid_paths:
            with self.assertRaises(InvalidJobException, msg=f'{job_path} gets parsed correctly but should fail') as assertion_error:
                job = Job(job_path)

            print(f'{str(assertion_error.exception.args[0]):40} ==> {assertion_error.exception.args[1]}')
