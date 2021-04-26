import datetime
from pathlib import Path
from unittest import TestCase

from pycron import SettingsSingleton
from pycron.job_discovery.folder_discovery import JobFolderScanner
from pycron.persistance.pickle_persistence import MemStore


class TestFolderDiscovery(TestCase):
    def setUp(self) -> None:
        self.test_folder = test_folder = Path('test_folder').absolute()
        test_folder.mkdir(exist_ok=True)

        # Change location of jobs folder before initializing the discoverer
        self.settings = settings = SettingsSingleton.get_settings()
        settings.set_jobs_folder(test_folder)

        explorer = JobFolderScanner(MemStore())
        self.explorer = explorer

        self.create_jobs()

    def tearDown(self) -> None:
        self._recursive_delete(self.test_folder)

    def _recursive_delete(self, path: Path):
        for sub_path in path.iterdir():
            if sub_path.is_dir():
                self._recursive_delete(sub_path)
            else:
                sub_path.unlink()
        path.rmdir()

    def create_jobs(self):
        self.jobs = jobs = [
            self.test_folder / '1min/test.sh',
            self.test_folder / '2min/test.sh',
            self.test_folder / '1hour/test.sh',
            self.test_folder / '1day/test.sh',
            self.test_folder / '1day.sh',  # Should be ignored as it is not a valid job
        ]

        for job in jobs:
            job.parent.mkdir(parents=True, exist_ok=True)
            with open(job, 'w') as test_file:
                test_file.write('hello world')

    def test_correct_job_path(self):
        explorer = self.explorer

        self.assertEqual(self.test_folder, explorer.job_folder, msg='Job folder in the explorer should match the test_folder')

    def test_discovery(self):

        self.explorer.run_discovery()

        now = datetime.datetime.now().replace(microsecond=0)
        discovery_timestamp = self.explorer.last_check.replace(microsecond=0)

        # Test the timestamp is correctly set
        self.assertEqual(now, discovery_timestamp, msg='Discovery was not timestamped properly')

        # Test the correct number of jobs are discovered
        self.assertEqual(4, len(self.explorer.store.store), msg='There should be exactly 4 valid jobs in jobs folder')

        # Test the jobs with the correct index are created
        for job in self.explorer.store.store.keys():
            self.assertIn(job, [x.absolute() for x in self.jobs])
