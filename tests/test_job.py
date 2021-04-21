import unittest
from pathlib import Path
from typing import Dict, List

from pycron.jobs.jobs import Job
from settings import RELATIVE_JOB_FOLER


class TestJobs(unittest.TestCase):

    def setUp(self) -> None:
        self.created_jobs_files: List[Path] = []  # Maintain list of files to purge after tests

        print(f'setting up')
        self.jobs_folder = RELATIVE_JOB_FOLER

    def tearDown(self) -> None:
        self._purge_files()

    def _make_file(self, file: Path):
        file.write_text('')
        self.created_jobs_files.append(file)

    def _purge_files(self):
        for file_path in self.created_jobs_files:
            file_path.unlink()

    def _valid_file_test(self, file_path: Path) -> Job:
        self._make_file(file_path)
        job_obj = Job(file_path)
        self.assertTrue(isinstance(job_obj, Job))

        return job_obj

    def test_valid_min_jobs(self):
        job_path = self.jobs_folder / '1min' / '1min_test.sh'
        job_obj = self._valid_file_test(job_path)

    def test_valid_5min_jobs(self):
        job_path = self.jobs_folder / '5min' / '5min_test.sh'
        job_obj = self._valid_file_test(job_path)


if __name__ == '__main__':
    unittest.main()
