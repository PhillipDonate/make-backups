import paths
import winsound

_err_wav = paths.this_dir / 'error.wav'
_ok_wav = paths.this_dir / 'ok.wav'

def _play_sound(path):
    winsound.PlaySound(path, winsound.SND_ASYNC | winsound.SND_FILENAME)

def success(): _play_sound(_ok_wav)
def error(): _play_sound(_err_wav)
