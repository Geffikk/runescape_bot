import logging
import cv2 as cv

from time import sleep

from src.utils.constants import PROJECT_ABSOLUTE_PATH, LOGGING_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)


class FightState:
    LOCKED_MOB_TOOLTIP = 0.95

    LOCKED_MOB_ICON = cv.imread(f'{PROJECT_ABSOLUTE_PATH}/action_images/general/locked_mob.png', cv.IMREAD_COLOR)

    def __init__(self, window_offset, window_size):
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        self.screenshot = None
        self.stopped = False
        #self.click_history = click_history

    def update_screenshot(self, screenshot):
        self.screenshot = screenshot

    def stop(self):
        self.stopped = True

    def still_fighting(self):
        sleep(3.0)  # wait a second to let the fight start and update the screenshot

        result = cv.matchTemplate(self.screenshot, self.LOCKED_MOB_ICON, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        logger.info(f'Locked mob match value: {max_val}')

        if max_val >= self.LOCKED_MOB_TOOLTIP:
            return True

        return False