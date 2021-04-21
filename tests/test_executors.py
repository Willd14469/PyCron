from pathlib import Path

from pycron.executor.folder_executor import FolderExecutor
from pycron.jobs.jobs import Job
from settings import RELATIVE_JOB_FOLER

test = FolderExecutor(RELATIVE_JOB_FOLER, None)
test_job = Job(Path(r'/testing/1min/test1.bat'))

test.execute_job(test_job)