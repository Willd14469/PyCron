from pathlib import Path
from unittest import TestCase

from pycron import SettingsSingleton


class TestSettings(TestCase):
    def setUp(self) -> None:
        self.settings = SettingsSingleton.get_settings()

        self.test_ini = Path('test.ini')
        with open(self.test_ini, 'w') as test_ini_file:
            test_ini_file.write("""[Timings]
# sleep duration between checking if a jobs needs to execute
SLEEP_DURATION = 99

# check the jobs folder every x minutes
CHECK_FOR_NEW_JOBS_EVERY = 99

# If a job fails, retry in x minutes
JOB_FAIL_TIMEOUT_PERIOD_MINUTES = 99

[Folders]
JOBS_FOLDER = helloworld
LOGS_FOLDER = helloworld
PERSISTENCE_FILE = helloworld

[Logging]
LOG_LEVEL = NOTSET""")

        self.test_folder = test_folder = Path('test_folder')
        if not self.test_folder.exists():
            self.test_folder.mkdir()

        self.dummy_folder = Path('BippidiBop')

    def test_default_file(self):
        """
        Test the default config loads correctly
        """

        settings = self.settings

        self.assertEqual(settings.loaded_file, settings.default_ini, 'Did not load the correct default file.')

    def test_update_config_from_file(self):
        """
        Test loading different config file
        """
        settings = self.settings

        settings.reload_config_from_file(self.test_ini.absolute())

        self.assertEqual(settings.loaded_file, self.test_ini.absolute(), 'Did not load the correct file.')

        self.assertEqual(settings.CHECK_FOR_NEW_JOBS_EVERY, 99)
        self.assertEqual(settings.SLEEP_DURATION, 99)
        self.assertEqual(settings.JOBS_FOLDER, Path('helloworld').absolute(), msg='Jobs Folder')
        self.assertEqual(settings.LOGS_FOLDER, Path('helloworld').absolute(), msg='Logs Folder')
        self.assertEqual(settings.PERSISTENCE_FILE, Path('helloworld').absolute(), msg='Persistence File')

    def test_set_job_folder(self):
        """
        Test setting job folder manually
        """
        settings = self.settings

        settings.set_jobs_folder(self.test_folder.absolute())

        self.assertEqual(settings.JOBS_FOLDER, self.test_folder.absolute(), msg='Job folder does not match')

    def test_set_log_folder(self):
        """
        Test setting log folder manually
        """
        settings = self.settings

        settings.set_logs_folder(self.test_folder.absolute())

        self.assertEqual(settings.LOGS_FOLDER, self.test_folder.absolute(), msg='Log folder does not match')

    def test_set_folder_error(self):
        """
        Tests set job folder errors if folder does not exist
        """

        settings = self.settings

        self.assertRaises(AssertionError, settings.set_jobs_folder, folder=self.dummy_folder)

        self.assertRaises(AssertionError, settings.set_logs_folder, folder=self.dummy_folder)

    def tearDown(self) -> None:
        # Delete test ini file
        self.test_ini.unlink()
        self.test_folder.rmdir()
