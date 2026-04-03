import paths
import sys

if sys.platform == 'win32':
    import winsound
    def _play_sound(path):
        winsound.PlaySound(str(path), winsound.SND_FILENAME)
else:
    def _play_sound(path):
        pass

_err_wav = paths.this_dir / 'error.wav'
_ok_wav = paths.this_dir / 'ok.wav'

def success(): _play_sound(_ok_wav)
def error(): _play_sound(_err_wav)
