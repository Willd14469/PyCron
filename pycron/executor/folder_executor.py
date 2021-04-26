import logging
import subprocess
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from threading import Thread, Lock
from time import sleep

from rich.logging import RichHandler

from pycron import settings
from pycron.job_discovery.folder_discovery import JobFolderScanner
from pycron.jobs.jobs import Job
from pycron.persistance.pickle_persistence import MemStore


# from pycron.settings import LOG, SLEEP_DURATION, RELATIVE_LOGS_FOLDER, LOGGING_LEVEL


class FolderExecutor:
    """
    Serves as base class executor for pycron

    Purpose: Execute jobs when needed

            Coordinates with the store and the job discovery as well
    """

    def __init__(self, nuke_persistence):

        self.store = MemStore(nuke_persistence)
        self.job_parser = JobFolderScanner(self.store)

        self.store_lock = Lock()

        logging.basicConfig(
            level=settings.LOG_LEVEL,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )

        logging.addLevelName(self.store.JOB_FAILED, 'JOB FAILED')
        logging.addLevelName(self.store.JOB_SUCCEEDED, 'JOB SUCCEEDED')

        file_handler = TimedRotatingFileHandler(settings.LOGS_FOLDER / 'job_status.log',
                                                when='H',
                                                interval=24,
                                                backupCount=30)
        file_handler.addFilter(JobFilter())  # Custom filter to only log job status data to file
        file_handler.setLevel(settings.LOG_LEVEL)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s \n'))
        settings.LOG.addHandler(file_handler)

    def loop(self):
        while True:
            runnables = self.store.runnable()

            self.parallel_job_runner(runnables)

            print(self.store.next_runnable())

            # update store after run
            self.job_parser.run_discovery()
            sleep(settings.SLEEP_DURATION)

    def parallel_job_runner(self, jobs: [Job]):
        number_of_threads = len(jobs)

        threads = []
        for job in jobs:
            job.lock()  # Job is locked by thread
            thread = Thread(target=self.execute_job, args=(job,))
            thread.name = job.relative_name
            thread.daemon = True
            thread.start()
            threads.append(thread)

        settings.LOG.debug(f'Finished creating {number_of_threads} threads')

    def execute_job(self, job: Job):
        """

        Async this

        :param job:
        :return:
        """
        settings.LOG.debug(f'Trying to execute: {(job.script_path.absolute())}')
        feedback: subprocess.CompletedProcess = subprocess.run(
            [(job.script_path.absolute())],
            shell=True,
            capture_output=True
        )
        with self.store_lock:
            if feedback.returncode == 0:
                settings.LOG.debug(f'{job.relative_name} succeeded')

                self.store.job_successful(job, feedback)
            else:
                settings.LOG.warning(f'{job.relative_name} failed...')
                self.store.job_failed(job, feedback)


class JobFilter(logging.Filter):
    acceptables = [MemStore.JOB_FAILED, MemStore.JOB_SUCCEEDED]

    def filter(self, record):
        if record.levelno in self.acceptables:
            return record
