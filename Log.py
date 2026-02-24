from rich.console import Console
from rich.text import Text
from rich.live import Live

console = Console()
red = '#ff0000'
green = '#00ff00'

def ok(message):
    console.print(f'[{green}](  OK  )[/]', Text(message))

def fail(message):
    console.print(f'[{red}](  !!  )[/]', Text(message))

def status(*args, **kwargs):
    kwargs.setdefault("spinner", "bouncingBall")
    kwargs.setdefault("spinner_style", green)
    return console.status(*args, **kwargs)

