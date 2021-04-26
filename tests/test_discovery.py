from pathlib import Path
from unittest import TestCase

from pycron import SettingsSingleton
from pycron.job_discovery.folder_discovery import JobFolderScanner
from pycron.persistance.pickle_persistence import MemStore


class TestFolderDiscovery(TestCase):
    def setUp(self) -> None:
        self.test_folder = test_folder = Path('test_folder').absolute()
        test_folder.mkdir(exist_ok=True)

        explorer = JobFolderScanner(MemStore())

        settings = SettingsSingleton.get_settings()
        settings.set_jobs_folder(test_folder)

        self.explorer = explorer

        self.create_jobs()

    def tearDown(self) -> None:
        # self.test_folder.rmdir()
        ...

    def create_jobs(self):
        jobs = [
            self.test_folder / '1min/test.sh',
            self.test_folder / '2min/test.sh',
        ]

        for job in jobs:

            job.parent.mkdir(parents=True, exist_ok=True)
            with open(job, 'w') as test_file:
                test_file.write('hello world')

    def test_discovery(self):
        self.explorer.run_discovery()