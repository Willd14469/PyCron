# PyCron

**PyCron** is an alternative to using cron as cron is not currently supported by snaps on Ubuntu Core. This project came
about due to the need to have scripts run on a tight schedule and easily be able to get feedback.

# Features

- No job manifest file needed!
  
PyCron operates by using the folder names of the jobs instead of having to link scripts in a manifest file.

<br>

- JSON based file log reporting the status of each job run.

PyCron provides a log of each job execution, including stdout and stderr, and other useful information about the job.

<br>

- Job execution persistence

PyCron provides a persistence layer to save the next needed execution of a job so if the scheduled timeslot was missed
then the job is executed next time the service is active. This provides protection against crashes and job failures.

<br>

- Re-runs failed jobs every x minutes

PyCron provides a mechanism to rerun failed jobs after a set amount of time instead of the normal schedule in the event
a script fails (Say due to internet outage). The shortened schedule ensures the script can be correctly run as soon as
the resource is restored.

<br>

# Installation

Install with included setuptools config. 

`pip install .` will install PyCron.

## Uninstallation

`pip uninstall pycron`

# Running

PyCron comes with multiple methods of launching it.

### Manually

`python -m pycron.main -c <<ini_config_file>>`

### Included script

`pycron -c <<ini_config_file>>`

## CLI Options
