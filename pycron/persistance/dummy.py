import datetime
import json
import pickle
import subprocess
from threading import Thread

from pycron.jobs.jobs import Job
from settings import LOG, PERSISTANCE_FILE


class MemStore:
    """
    Serves as a persistant store of job status data

    Dummy is a memory only version primarily for testing.
    """

    JOB_FAILED = 45
    JOB_SUCCEEDED = 40

    def __init__(self):
        self.store = self.deserialize_store()

        # # self.store = {}
        #
        # self.persistance_file = open(PERSISTANCE_FILE, 'w')

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

    def delete_old_job(self, script_path):
        ...

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
            LOG.log(self.JOB_FAILED, json.dumps(job_status, indent=True))
        else:
            LOG.log(self.JOB_SUCCEEDED, json.dumps(job_status, indent=True))

    def next_runnable(self):
        """Debug feature to get the next runtime in minutes for each job"""
        now = datetime.datetime.now()
        next_executions = [job.next_execution for job in self.store.values()]
        return [(next_exe - now).seconds for next_exe in next_executions]

    def trigger_threaded_write(self):
        """
        Runs the threaded job to write the store to a file

        TODO make this a singleton thread and send the store to the thread for each write instead of spawning a new thread for each job result
        """
        LOG.info('Writing store to file...')
        write_thread = Thread(target=self.serialize_store, args=[self.store], name=f'log_writer')
        write_thread.start()
        write_thread.join()
        LOG.info('Finished storing.')

    def serialize_store(self, store):
        with open(PERSISTANCE_FILE, 'wb') as cache:
            pickle.dump(store, cache)

    def deserialize_store(self) -> dict:
        if not PERSISTANCE_FILE.is_file():
            return {}
        with open(PERSISTANCE_FILE, 'rb') as cache:
            LOG.info('Loading previous state from file...')
            store = pickle.load(cache)
            for job in store.values():
                job.unlock()

        return store
