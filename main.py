from main_machine import MainMachine
from archive_machine import ArchiveMachine
from pathlib import Path
from time import sleep
from rich.text import Text
import sys
import argparse
import importlib.util
import log
import paths
import sound

def load_config(arg_config):
    cfg_path = Path(arg_config) if arg_config else paths.this_dir / 'config.py'

    if not cfg_path.is_file():
        log.console.print(Text(f'Could not load config: {cfg_path}'))
        return None

    spec = importlib.util.spec_from_file_location('config', cfg_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def report_error():
    message = f'[{log.red}]One or more problems occurred![/]'

    with log.status(message, spinner_style=log.red):
        sound.error()

    log.fail(message)

def report_success():
    message = f'[{log.green}]All done![/]'

    with log.status(message):
        sound.success()

    log.ok(message)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    args = parser.parse_args()
    config = load_config(args.config)

    if not config:
        return 1

    paths.hydrate(config)

    workers = [
        ArchiveMachine(name, steps) for name, steps in config.archives.items()
    ]

    main_machine = MainMachine(
        prep_steps=getattr(config, 'prepare', []),
        finish_steps=getattr(config, 'finish', []),
        workers=workers
    )

    main_machine.go()

    if main_machine.failed:
        report_error()
        return 1
    
    report_success()
    return 0

if __name__ == "__main__":
    sys.exit(main())
