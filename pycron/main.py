from pathlib import Path

from pycron.executor.folder_executor import FolderExecutor
from settings import LOG, SLEEP_DURATION, JOBS_FOLDER


class MainThread:
    MIN_SLEEP_DURATION = 0.5
    MAX_SLEEP_DURATION = 1800

    def __init__(self):
        self.job_check_interval = SLEEP_DURATION
        self.jobs_folder = Path(JOBS_FOLDER).absolute()

        self.param_validation()

        self.executor: FolderExecutor = FolderExecutor(self.jobs_folder, None)

        self.main_log = LOG

    def param_validation(self):
        if not self.MIN_SLEEP_DURATION < self.job_check_interval < self.MAX_SLEEP_DURATION:
            raise AttributeError(
                f'Invalid sleep duration {self.job_check_interval}; must be between {self.MIN_SLEEP_DURATION} and {self.MAX_SLEEP_DURATION}')

        if not self.jobs_folder.is_dir():
            raise NotADirectoryError(f'{self.jobs_folder} is not a directory!')

    def startup_status(self):
        self.main_log.info(f'--- Main settings ---')
        self.main_log.info(f'Job folder         -> {self.jobs_folder}')
        self.main_log.info(f'Job check interval -> {self.job_check_interval} seconds')

    def run(self):
        self.executor.loop()


if __name__ == '__main__':
    try:
        main_thread = MainThread()
        main_thread.startup_status()
        main_thread.run()
    except Exception as excp:
        LOG.exception(excp.args)
