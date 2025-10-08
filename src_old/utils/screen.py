import pyautogui


def locate_center_on_screen(path, confidence=0.8, region=None):
    try:
        return pyautogui.locateCenterOnScreen(path, confidence=confidence, region=region)
    except Exception:
        return None


def locate_on_screen(path, confidence=0.8, region=None):
    try:
        return pyautogui.locateOnScreen(path, confidence=confidence, region=region)
    except Exception:
        return None