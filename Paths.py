from pathlib import Path
import shutil
import sys

this_dir = Path(sys.argv[0]).resolve().parent
zipper = None
age = None

def hydrate(config):
    global zipper, age
    paths = getattr(config, 'paths', {})
    zipper = Path(shutil.which('tar') or '')
    age = Path(paths.get('age', this_dir / 'age.exe'))
