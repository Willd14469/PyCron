import datetime
import json
import pickle
import subprocess
from pathlib import Path
from threading import Thread
from typing import List

from pycron import settings
from pycron.jobs.jobs import Job


class MemStore:
    """
    Serves as a persistant store of job status data

    Uses pickle to save the data to a file each time a job status method is called
    """

    JOB_FAILED = 45
    JOB_SUCCEEDED = 40

    def __init__(self, nuke_persistence=False):
        self.store = self.deserialize_store(nuke_persistence)

    def fetch(self, script_path):
        if script_path in self.store:
            return self.store[script_path]

        return self.create_new_job(script_path)

    def active_jobs(self):
        ...

    def create_new_job(self, script_path):
        new_job = Job(script_path)
        self.store[script_path] = new_job
        return new_job

    def check_for_non_existent_job(self, current_existing_scripts: List[Path]):
        """
        Purge any jobs that exist in the store but that have been removed from the script list.

        Triggered by the discovery module.
        :param current_existing_scripts: List of Paths that are currently in the job directory
        """
        stored_job_keys = self.store.keys()

        removed_jobs = [x for x in stored_job_keys if x not in current_existing_scripts]

        for job in removed_jobs:
            settings.LOG.warning(f'{job} not longer exists in job dir, removing now...')
            del self.store[job]

        self.trigger_threaded_write()

    def runnable(self):
        now = datetime.datetime.now()

        # list of jobs that are unlocked and past the next runnable threshold
        # Locked jobs are the ones already targeted by a thread
        runnable_jobs = [job for job in self.store.values() if job.next_execution < now and not job.locked]

        return runnable_jobs

    def job_successful(self, job: Job, job_status):
        job.success()
        self._log_job_status(job, job_status, False)
        self.trigger_threaded_write()
        # Update persistant store disk data

    def job_failed(self, job: Job, job_status: subprocess.CompletedProcess):
        job.fail()
        self._log_job_status(job, job_status, True)
        self.trigger_threaded_write()

    def _log_job_status(self, job: Job, job_status: subprocess.CompletedProcess, failed):
        job_status = {
            'file': str(job.relative_name),
            'uuid': str(job.job_uuid),
            'status_code': job_status.returncode,
            'output': job_status.stdout.decode('utf-8'),
            'error': job_status.stderr.decode('utf-8'),
            'next_run': job.next_execution.isoformat(),
            'reason_for_run': job.run_reason.value,
            'number_of_failed_attempts': job.failed_attempts,
            'begun_at': job.locked_at.isoformat(),
            'ended_at': job.unlocked_at.isoformat(),
            'runtime': job.runtime
        }
        if failed:
            settings.LOG.log(self.JOB_FAILED, json.dumps(job_status, indent=True))
        else:
            settings.LOG.log(self.JOB_SUCCEEDED, json.dumps(job_status, indent=True))

    def next_runnable(self):
        """Debug feature to get the next runtime in minutes for each job"""
        now = datetime.datetime.now()
        next_executions = {job.relative_name: f'{(job.next_execution - now).seconds}' for job in self.store.values()}
        settings.LOG.debug(f'Next runtimes: {next_executions}')
        # return [(next_exe - now).seconds for next_exe in next_executions]

    def trigger_threaded_write(self):
        """
        Runs the threaded job to write the store to a file

        TODO make this a singleton thread and send the store to the thread for each write instead of spawning a new thread for each job result
        """
        settings.LOG.info('Writing store to file...')
        write_thread = Thread(target=self.serialize_store, args=[self.store], name=f'log_writer')
        write_thread.start()
        write_thread.join()
        settings.LOG.info('Finished storing.')

    @staticmethod
    def serialize_store(store):
        """
        Writes store to persistence layer
        """
        with open(settings.PERSISTENCE_FILE, 'wb') as cache:
            pickle.dump(store, cache)

    @staticmethod
    def deserialize_store(nuke_persistence) -> dict:
        """
        Reads store from persistence layer
        """

        if nuke_persistence:
            settings.LOG.warning('Deleting persistence file, starting fresh')
            settings.PERSISTENCE_FILE.unlink(missing_ok=True)  # Delete persistence file to start fresh

        if not settings.PERSISTENCE_FILE.is_file():
            return {}
        with open(settings.PERSISTENCE_FILE, 'rb') as cache:
            settings.LOG.info('Loading previous state from file...')
            store = pickle.load(cache)
            for job in store.values():
                job.unlock()

        return store
