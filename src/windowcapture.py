import numpy as np
import pywinctl as pwc
import mss
from threading import Thread, Lock


class WindowCapture:
    stopped = True
    lock = None
    screenshot = None
    w = 0
    h = 0
    window = None
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None):
        """Capture a given window or the entire screen"""
        self.lock = Lock()

        if window_name is None:
            # Capture the primary screen
            self.window = None
            monitor = mss.mss().monitors[1]
            self.offset_x = 0
            self.offset_y = 0
            self.w = monitor["width"]
            self.h = monitor["height"]
        else:
            # Find the target window
            try:
                self.window = pwc.getWindowsWithTitle(window_name)[0]
            except IndexError:
                raise Exception(f"Window not found: {window_name}")

            # Ensure window is not minimized or hidden
            if not self.window.isVisible or self.window.isMinimized:
                raise Exception(f"Window '{window_name}' is not visible")

            x, y, w, h = self.window.left, self.window.top, self.window.width, self.window.height
            self.offset_x, self.offset_y, self.w, self.h = x, y, w, h

    def get_screenshot(self):
        """Capture screenshot of the window or screen as numpy array"""
        with mss.mss() as sct:
            if self.window is None:
                monitor = sct.monitors[1]
            else:
                monitor = {
                    "left": self.offset_x,
                    "top": self.offset_y,
                    "width": self.w,
                    "height": self.h,
                }

            img = np.array(sct.grab(monitor))
            # Drop alpha channel for OpenCV compatibility
            img = img[..., :3]
            img = np.ascontiguousarray(img)
            return img

    @staticmethod
    def list_window_names():
        """List all visible window titles"""
        for w in pwc.getAllWindows():
            if w.title and w.isVisible:
                print(f"{hex(w._hWnd)} {w.title}")

    def get_screen_position(self, pos):
        """Translate window-relative coordinates to absolute screen coordinates"""
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

    # threading support
    def start(self):
        """Start background screenshot thread"""
        self.stopped = False
        t = Thread(target=self.run, daemon=True)
        t.start()

    def stop(self):
        """Stop background thread"""
        self.stopped = True

    def run(self):
        """Continuously capture screenshots"""
        while not self.stopped:
            screenshot = self.get_screenshot()
            with self.lock:
                self.screenshot = screenshot