from pathlib import Path

import Run
import winsound

_err_wav = Run.get_exe_dir() / 'error.wav'
_ok_wav = Run.get_exe_dir() / 'ok.wav'

def _play_sound(path):
    winsound.PlaySound(path, winsound.SND_ASYNC | winsound.SND_FILENAME)

def success(): _play_sound(_ok_wav)
def error(): _play_sound(_err_wav)
