import unittest

from pycron.job_discovery.folder_name import JobFolderScanner
from pycron.persistance.dummy import MemStore
from settings import RELATIVE_JOB_FOLER


class TestJobs(unittest.TestCase):

    def test_persistence(self):
        store = MemStore()
        discovery = JobFolderScanner(RELATIVE_JOB_FOLER, store)

        discovery.run_discovery()

        store.trigger_threaded_write()
