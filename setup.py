from setuptools import setup

setup(
    name='pycron',
    version='0.1.0',
    packages=['pycron', 'pycron.executor', 'pycron.interval', 'pycron.job_discovery', 'pycron.persistance',
              'pycron.jobs'],
    url='',
    license='',
    author='Will Derriman',
    author_email='',
    description='Cron inspired implementation of a job scheduler and executor',
    install_requires=[
        'rich'
    ],
    scripts=[],

)
