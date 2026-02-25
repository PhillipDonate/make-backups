from pathlib import Path
from rich.console import Console
from rich.text import Text

console = Console()
red = '#ff0000'
green = '#00ff00'

def ok(*args, **kwargs):
    console.print(f'[{green}](  OK  )[/]', *args, **kwargs)

def fail(*args, **kwargs):
    console.print(f'[{red}](  !!  )[/]', *args, **kwargs)

def status(*args, **kwargs):
    kwargs.setdefault("spinner", "bouncingBall")
    kwargs.setdefault("spinner_style", green)
    return console.status(*args, **kwargs)

def append_size(text: Text, path: Path):
    size = path.stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            size = f'{size:.2f} {unit}'
            break
        size /= 1024
    text.append(Text('  ', style="dim grey50"))
    text.append(Text(size, style="dim italic grey50"))
