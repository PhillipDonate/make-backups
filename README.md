# MakeBackups

A lightweight, data-driven incremental archiver that automates routine file backups into compressed archives with no complex dependencies. Each backup is a standard archive in a format of your choosing (`.zip`, `.tar.xz`, `.tar.gz`), named by date for easy identification and recovery.

MakeBackups keeps things transparent and self-contained. Backups are plain archives openable with any standard tool, so you can trust your files are recoverable. Built with simplicity in mind, it started as a way to give non-technical family members reliable backups and has since grown to support encryption for long-term storage in untrusted locations.

![](demo.gif)

## Features

- Incremental archives automatically named and organized by date
- Automatic pruning of old archives by age or count
- Post-processing support via external tool execution
- Optional asymmetric encryption via [age](https://age-encryption.org)
- Simple, flexible Python-based configuration
- Runs from source or as a self-contained Windows executable

## Requirements

MakeBackups can be run directly from Python source or as a pre-built Windows executable.

**From source:**
- Python 3.x
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
4. Run `python <path-to-makebackups>/main.py`

**Windows executable:**
1. Download and extract the zip from the [Releases](../../releases) page
2. Create `config.py` — see [Configuration](#configuration)
3. Run `makebackups.exe`

A custom config file path can optionally be passed as a command line argument.

## Configuration

MakeBackups is configured via a `config.py` file placed in the same directory as the executable or script, or by passing `--config <path-to-config>` on the command line.

Two example configuration files are provided:
- [`example_config_simple.py`](example_config_simple.py) — a minimal setup to get started quickly
- [`example_config_full.py`](example_config_full.py) — all available options with documentation

## License

GPL-3.0 — see [LICENSE](LICENSE) for details.
