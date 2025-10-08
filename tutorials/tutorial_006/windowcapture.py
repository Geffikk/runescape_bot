import numpy as np
import mss
import pywinctl


class WindowCapture:
    def __init__(self, window_name=None):
        if window_name is None:
            self.win = None
            bbox = pywinctl.getAllScreens()[0]  # primary screen
            self.left, self.top = bbox.left, bbox.top
            self.w, self.h = bbox.width, bbox.height
        else:
            wins = pywinctl.getWindowsWithTitle(window_name)
            if not wins:
                raise RuntimeError(f"Window not found: {window_name}")
            self.win = wins[0]

            # get full window size
            self.left, self.top = self.win.left, self.win.top
            self.w, self.h = self.win.width, self.win.height

            # account for borders and title bar
            border_pixels = 8
            titlebar_pixels = 30
            self.left += border_pixels
            self.top += titlebar_pixels
            self.w -= border_pixels * 2
            self.h -= titlebar_pixels + border_pixels

        self.offset_x = self.left
        self.offset_y = self.top

        self.sct = mss.mss()
        self.monitor = {"left": self.left, "top": self.top, "width": self.w, "height": self.h}

    def get_screenshot(self):
        img = np.array(self.sct.grab(self.monitor))
        img = img[..., :3]  # drop alpha
        return np.ascontiguousarray(img)

    @staticmethod
    def list_window_names():
        for w in pywinctl.getAllWindows():
            if w.isVisible:
                print(w.title)

    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)