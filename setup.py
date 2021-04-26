from setuptools import setup

setup(
    name='pycron',
    version='0.1.6',
    packages=['pycron', 'pycron.executor', 'pycron.interval', 'pycron.job_discovery', 'pycron.persistance',
              'pycron.jobs'],
    url='',
    license='',
    author='Will Derriman',
    author_email='will.derriman@lettusgrow.org',
    description='Cron inspired implementation of a job scheduler and executor',
    install_requires=[
        'rich'
    ],
    scripts=['bin/pycron'],
    package_data={
        # Include the default config.ini file in the package
        "": ["config.ini"]
    }

)
