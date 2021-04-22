import unittest

from pycron.job_discovery.folder_discovery import JobFolderScanner
from pycron.persistance.pickle_persistence import MemStore
from pycron.settings import RELATIVE_JOB_FOLDER


class TestJobs(unittest.TestCase):

    def test_persistence(self):
        store = MemStore()
        discovery = JobFolderScanner(RELATIVE_JOB_FOLDER, store)

        discovery.run_discovery()

        store.trigger_threaded_write()
