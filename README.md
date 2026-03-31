# MakeBackups

A lightweight, data-driven incremental backup archiver written in Python.

![](demo.gif)

## Features

- Incremental archives automatically named and organized by date
- Automatic pruning of old archives by age or count
- Post-processing support via external tool execution
- Optional asymmetric encryption via [age](https://age-encryption.org)
- Simple, flexible Python-based configuration

## Requirements

MakeBackups can be run directly from Python source or as a pre-built Windows executable.

**From source:**
- Python 3.x (Tested on 3.11 and 3.12)
    - isodate
    - python-statemachine
    - rich

**Windows executable:**
- Download the pre-built package from the [Releases](../../releases) page — A Python install is not required.

## Installation

**From source:**
1. Clone the repo
2. Run `pip install isodate python-statemachine rich`
3. Create `config.py` — see [Configuration](#configuration)
4. Run `python main.py`

**Windows executable:**
1. Download and extract the zip from the [Releases](../../releases) page
2. Create `config.py` — see [Configuration](#configuration)
3. Run `makebackups.exe`

A custom config file path can optionally be passed as a command line argument.

## Configuration

MakeBackups is configured via `config.py` in the working directory, or a custom path can be specified with `--config <path>` on the command line.

Two example configuration files are provided:
- [`example_config_simple.py`](example_config_simple.py) — a minimal setup to get started quickly
- [`example_config_full.py`](example_config_full.py) — all available options with documentation

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.
