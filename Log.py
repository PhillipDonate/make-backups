from rich.console import Console
from rich.text import Text
from rich.live import Live
from time import sleep, monotonic
import msvcrt

console = Console()

def ok(message):
    console.print('[green]✓[/green]', Text(message))

def fail(message):
    console.print('[red]✘[/red]', Text(message))

def pause_for_failure(message):
    colors = ['red', 'bright_red']
    i = 0

    with Live(console=console, refresh_per_second=2) as live:
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()
                break

            color = colors[i % len(colors)]
            live.update(f'[{color}]✘ {message}[/{color}]')
            i += 1
            sleep(0.1)

def pause_for_success(message):
    colors = ['green', 'bright_green']
    i = 0

    end_time = monotonic() + 5

    with Live(console=console, refresh_per_second=2) as live:
        while monotonic() < end_time:
            color = colors[i % len(colors)]
            live.update(f'[{color}]✓ {message}[/{color}]')
            i += 1
            sleep(0.1)
