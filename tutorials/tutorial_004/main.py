import cv2 as cv
import numpy as np
import os
import mss
import pyautogui
from PIL import ImageGrab
import pygetwindow
import pywinctl


from time import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

title_query = "RuneScape"  # part of window title
#wins = pygetwindow.getWindowsWithTitle(title_query)
wins = pywinctl.getWindowsWithTitle(title_query)
if not wins:
    raise RuntimeError("Window not found")

win = wins[0]
#win.activate()
bbox = {"left": win.left, "top": win.top, "width": win.width, "height": win.height}

cv.namedWindow("Compute Vision", cv.WINDOW_NORMAL)
cv.resizeWindow('Compute Vision', 1400, 800)

sct = mss.mss()
monitor = sct.monitors[1]  # full screen (use [0] for all monitors)

t0 = time()
while True:
    frame = np.array(sct.grab(bbox))
    frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
    # drop alpha channel
    frame = frame[:, :, :3]

    fps = 1.0 / (time() - t0)
    t0 = time()
    cv.imshow("Capture", frame)
    cv.setWindowTitle("Capture", f"FPS {fps:.1f}")

    if cv.waitKey(1) & 0xFF == ord("q"):
        break

cv.destroyAllWindows()