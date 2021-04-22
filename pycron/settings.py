import logging
from pathlib import Path

"""
    All modular settings available to pycron
"""

LOG = logging.getLogger("main_log")
LOGGING_LEVEL = 'NOTSET'

SLEEP_DURATION = 1  # sleep duration between checking if a jobs needs to execute

CHECK_FOR_NEW_JOBS_EVERY = 5  # check the jobs folder every x minutes

JOB_FAIL_TIMEOUT_PERIOD_MINUTES = 2  # If a job fails, retry in x minutes

JOBS_FOLDER = './testing'  # read and write

LOGS_FOLDER = './logs'

PERSISTANCE_FILE = Path(__file__).parent.parent / 'persistance.pickle'

EXECUTOR_JOB_MANIFEST = 'executor_manifest'  # must be read and writable

RELATIVE_JOB_FOLDER = Path(__file__).parent.parent / JOBS_FOLDER
RELATIVE_LOGS_FOLDER = Path(__file__).parent.parent / LOGS_FOLDER
