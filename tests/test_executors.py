from pathlib import Path

from pycron.executor.folder_executor import FolderExecutor
from pycron.jobs.jobs import Job
from pycron.settings import RELATIVE_JOB_FOLDER

test = FolderExecutor(RELATIVE_JOB_FOLDER, None)
test_job = Job(Path(r'/testing/1min/test1.bat'))

test.execute_job(test_job)