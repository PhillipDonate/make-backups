from pathlib import Path
import subprocess
import sys

def run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ):
    result = subprocess.run(args=cmd, stdout=stdout, stderr=stderr)
    return result.returncode

def get_exe_dir() -> Path:
    return Path(sys.argv[0]).resolve().parent