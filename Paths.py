from pathlib import Path
import shutil
import sys

this_dir = Path(sys.argv[0]).resolve().parent
zipper = None
age = None

def _get_exe_path(paths, exe):
    return Path(paths.get(exe) or shutil.which(exe) or exe)

def hydrate(config):
    global zipper, age
    paths = getattr(config, 'paths', {})
    zipper = _get_exe_path(paths, 'tar')
    age = _get_exe_path(paths, 'age')
