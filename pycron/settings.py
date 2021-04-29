import logging
import os
from configparser import ConfigParser
from pathlib import Path

"""
    All modular settings available to pycron
"""

SETTINGS_OBJ = None


class SettingsSingleton:
    """
    Provides an interface to obtain a singleton object of the settings class. Provides a method to update settings and
    propagate those changes throughout the modules.
    """

    @staticmethod
    def get_settings():
        global SETTINGS_OBJ

        if SETTINGS_OBJ:
            return SETTINGS_OBJ

        settings = _Settings()
        SETTINGS_OBJ = settings
        return SETTINGS_OBJ


class _Settings:
    """
    Do not import directly. Use singleton class to retrieve the single instance of settings
    """
    default_ini = (Path(__file__).parent / 'config.ini').absolute()

    def __init__(self):
        # init logging
        self.LOG = logging.getLogger("main_log")

        self.SLEEP_DURATION = None
        self.CHECK_FOR_NEW_JOBS_EVERY = None
        self.JOB_FAIL_TIMEOUT_PERIOD_MINUTES = None
        self.JOBS_FOLDER = None
        self.LOGS_FOLDER = None
        self.PERSISTENCE_FILE = None
        self.LOG_LEVEL = None

        self.loaded_file = None

        self.load_config_params(self.default_ini)

    def load_config_params(self, ini_file: Path):
        ini_parser = ConfigParser()
        ini_parser.read(ini_file)

        self.LOG.info(f'Loading config from {ini_file}')

        # sleep duration between checking if a jobs needs to execute
        self.SLEEP_DURATION = int(ini_parser['Timings'].get('SLEEP_DURATION', '1'))

        # check the jobs folder every x minutes
        self.CHECK_FOR_NEW_JOBS_EVERY = int(ini_parser['Timings'].get('CHECK_FOR_NEW_JOBS_EVERY', '15'))

        # If a job fails, retry in x minutes
        self.JOB_FAIL_TIMEOUT_PERIOD_MINUTES = int(ini_parser['Timings'].get('JOB_FAIL_TIMEOUT_PERIOD_MINUTES', '2'))

        # read and write
        self.JOBS_FOLDER = Path(ini_parser['Folders'].get('JOBS_FOLDER', '/etc/pycron/jobs')).absolute()

        self.LOGS_FOLDER = Path(ini_parser['Folders'].get('LOGS_FOLDER', '/etc/pycron/logs')).absolute()

        self.PERSISTENCE_FILE = Path(ini_parser['Folders'].get('PERSISTENCE_FILE', 'persistence.pickle')).absolute()

        self.LOG_LEVEL = ini_parser['Logging'].get('LOG_LEVEL', 'NOTSET')

        self.loaded_file = ini_file

    def reload_config_from_file(self, file_path: str):
        ini_file = Path(file_path).absolute()
        assert ini_file.is_file(), f'{ini_file} does not exist'

        print(f'Loaded config from file: {ini_file}')
        self.load_config_params(ini_file)

    def set_jobs_folder(self, folder: str):
        job_path = Path(folder).absolute()
        assert job_path.is_dir(), f'{job_path} does not exist'

        self.JOBS_FOLDER = job_path

    def set_logs_folder(self, folder: str):
        job_path = Path(folder).absolute()
        assert job_path.is_dir(), f'{job_path} does not exist'

        self.LOGS_FOLDER = job_path

    def set_persistence_file_location(self, file: str):
        job_path = Path(file).absolute()
        assert job_path.is_file(), f'{job_path} does not exist'

        self.PERSISTENCE_FILE = job_path

    def summaries_settings(self):
        params = vars(self)

        for k, v in params.items():
            print(f'{k:35} ==> {v}')
            # Pad the key value up to 35 chars long
