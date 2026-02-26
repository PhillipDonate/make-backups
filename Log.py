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
