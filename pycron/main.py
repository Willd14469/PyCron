import argparse
import os
from pathlib import Path

from pycron import settings


from pycron.coordinator import MainThread


def relative_to_absolute(path: str) -> Path:
    return Path(path).absolute()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nuke', action='store_true')
    parser.add_argument('-t', '--target', action='store', help='Jobs folder to target')
    parser.add_argument('-l', '--log-folder', action='store', help='Log folder to target')
    parser.add_argument('-c', '--config-file', action='store', help='Config file to target')

    args = vars(parser.parse_args())
    print(args)

    if args['config_file']:
        settings.reload_config_from_file(args['config_file'])

    if args['target']:
        absolute_path = relative_to_absolute(args['target'])
        settings.set_jobs_folder(absolute_path)

    if args['log_folder']:
        absolute_path = relative_to_absolute(args['log_folder'])
        settings.set_logs_folder(absolute_path)

    settings.summaries_settings()

    # try:
    main_thread = MainThread(nuke_persistence=args['nuke'])
    main_thread.run()
    # except Exception as excp:
    #     LOG.exception(excp.args)
