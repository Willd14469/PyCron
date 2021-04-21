import logging
from pathlib import Path

from rich.logging import RichHandler

LOG = logging.getLogger("main_log")

SLEEP_DURATION = 1  # sleep duration between checking if a jobs needs to execute

CHECK_FOR_NEW_JOBS_EVERY = 5  # check the jobs folder every x minutes

JOB_FAIL_TIMEOUT_PERIOD_MINUTES = 2  # If a job fails, retry in x minutes

JOBS_FOLDER = './testing'  # read and write

LOGS_FOLDER = './logs'

PERSISTANCE_FILE = Path(__file__).parent / 'persistance.pickle'

EXECUTOR_JOB_MANIFEST = 'executor_manifest'  # must be read and writable

RELATIVE_JOB_FOLER = Path(__file__).parent / JOBS_FOLDER
RELATIVE_LOGS_FOLDER = Path(__file__).parent / LOGS_FOLDER
