from pathlib import Path
import os
import shutil
import importlib.util
from ArchiveMachine import ArchiveMachine
import Sound
import Run
import Log

def load_config():
    cfg_file = 'Config.py'
    cfg_path = Run.get_exe_dir() / cfg_file

    if not cfg_path.exists():
        raise FileNotFoundError(f'Not found: {cfg_file}')

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
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

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
    config = load_config()

    do_global_ops(config.prepare)

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

    do_global_ops(config.finish)  
    failed = [m for m in machines if m.is_failed()]

    if failed:
        Sound.error()
        Log.pause_for_failure('One or more problems occurred!')
    else:
        Sound.success()
        Log.pause_for_success('All done!')

if __name__ == "__main__":
    main()