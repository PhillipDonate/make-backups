from MainMachine import MainMachine
from ArchiveMachine import ArchiveMachine
from pathlib import Path
from time import sleep
import sys
import argparse
import importlib.util
import Log
import Paths
import Sound

def load_config(arg_config):
    cfg_path = Path(arg_config) if arg_config else Paths.this_dir / 'config.py'

    if not cfg_path.is_file():
        Log.console.print(f'Could not load config: {cfg_path}')
        return None

    spec = importlib.util.spec_from_file_location('config', cfg_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def report_error():
    with Log.status(f'[{Log.red}]One or more problems occurred![/]', spinner_style=Log.red):
        Sound.error()
        input()

def report_success():
    with Log.status(f'[{Log.green}]All done![/]'):
        Sound.success()
        sleep(3)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    args = parser.parse_args()
    config = load_config(args.config)

    if not config:
        return 1

    Paths.hydrate(config)

    workers = [
        ArchiveMachine(name, steps) for name, steps in config.archives.items()
    ]

    main_machine = MainMachine(
        prep_steps=getattr(config, 'prepare', []),
        finish_steps=getattr(config, 'finish', []),
        machines=workers
    )

    main_machine.go()

    if main_machine.is_failed():
        report_error()
        return 1
    
    report_success()
    return 0

if __name__ == "__main__":
    sys.exit(main())
