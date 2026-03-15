from ArchiveMachine import ArchiveMachine
from pathlib import Path
from time import sleep
import argparse
import importlib.util
import Log
import os
import Run
import shutil
import Sound

def load_config(arg_config):
    cfg_path = None
    
    if arg_config:
        cfg_path = Path(arg_config)
    else:
        cfg_path = Run.get_exe_dir() / 'Config.py'

    if not cfg_path.exists():
        raise FileNotFoundError(f'Not found: {cfg_path}')

    spec = importlib.util.spec_from_file_location('config', cfg_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

def op_rmdir(item):
    path = Path(item['path'])
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=item.get('ignore_errors'))

def op_mkdir(item):
    path = Path(item['path'])
    if path.is_dir():
        return
    os.mkdir(path)

def do_global_ops(items):
    for item in items:
        op = item.get('op')
        match(op):
            case 'rmdir':
                op_rmdir(item)
            case 'mkdir':
                op_mkdir(item)
            case _:
                raise ValueError(f'Unknown op: {op}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    args = parser.parse_args()
    config = load_config(args.config)

    do_global_ops(getattr(config, 'prepare', []))

    machines = [
        ArchiveMachine(name, steps)
            for name, steps in config.archives.items()
    ]

    while True:
        active = [m for m in machines if not m.is_finished()]

        if not active:
            break

        for m in active:
            m.next()

    do_global_ops(getattr(config, 'finish', []))

    failed = [m for m in machines if m.is_failed()]

    if failed:
        Sound.error()
        with Log.status(f'[{Log.red}]One or more problems occurred![/]', spinner_style=Log.red):
            input()
    
    else:
        Sound.success()
        with Log.status(f'[{Log.green}]All done![/]'):
            sleep(3)

if __name__ == "__main__":
    main()