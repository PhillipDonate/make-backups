from pathlib import Path
import sys

this_dir = Path(sys.argv[0]).resolve().parent
zipper = None
age = None

def hydrate(config):
    global zipper, age
    paths = getattr(config, 'paths', {})
    zipper = Path(paths.get('zipper', this_dir / '7za.exe'))
    age = Path(paths.get('age', this_dir / 'age.exe'))
