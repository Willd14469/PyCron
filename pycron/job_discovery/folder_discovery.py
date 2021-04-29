import datetime
from pathlib import Path
from typing import List

from pycron import settings
from pycron.interval.minutes import Minutes
from pycron.jobs.jobs import InvalidJobException
from pycron.persistance.pickle_persistence import MemStore


# from pycron.settings import LOG, CHECK_FOR_NEW_JOBS_EVERY


class JobFolderScanner:
    """
    Serves as base class for determining what jobs exist

    Purpose: Scan for jobs and determine how often they need to run

    Checks persistant store to see if the job already exists in the store.
    """

    def __init__(self, store: MemStore):
        self.job_folder: Path = settings.JOBS_FOLDER
        self.store = store

        self.last_check = None
        self.check_interval = Minutes(every=settings.CHECK_FOR_NEW_JOBS_EVERY)

    def scan_folder(self):
        """
        Get all folders in scripts directory
        :return:
        """
        files = []
        dirs = []
        for item in self.job_folder.glob('**'):

            if item.is_dir():
                dirs.append(item)
            elif item.is_file():
                files.append(item)
            else:
                settings.LOG.warning(f'Unclassified item: {item}')

        return files, dirs

    def _collect_all_scripts(self) -> List[Path]:
        """
        Get all scripts and return them
        :return: []
        """
        files, folders = self.scan_folder()
        for dir in folders:
            for file in dir.iterdir():
                if file.is_file():
                    files.append(file)

        return files

    def _check_for_jobs(self):

        settings.LOG.info(f'Checking for jobs changes...')
        all_scripts = self._collect_all_scripts()
        for path in all_scripts:
            try:
                # Create record of job in store
                self.store.fetch(path)
            except InvalidJobException as invalid_job_excp:
                settings.LOG.warning(f'Invalid Script {invalid_job_excp.args[0]}, reason: {invalid_job_excp.args[1]}')

        # Purge old jobs that no longer exist
        self.store.check_for_non_existent_job(all_scripts)

    def run_discovery(self):
        """
        Callable in a loop and will only run check_for_jobs if it is expected
        """
        now = datetime.datetime.now()

        if now > self.check_interval.next_time(self.last_check) or self.last_check is None:
            self._check_for_jobs()
            self.last_check = now
