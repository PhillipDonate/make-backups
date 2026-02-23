import Run
import winsound

def success():
    winsound.Beep(700, 80)
    winsound.Beep(900, 80)
    winsound.Beep(1100, 120)

def error():
    winsound.Beep(500, 120)
    winsound.Beep(350, 150)
    winsound.Beep(250, 180)
