import cv2 as cv

from time import sleep

from src.utils.constants import PROJECT_ABSOLUTE_PATH


class HealState:
    ACTION_IMAGES_PATH = f'{PROJECT_ABSOLUTE_PATH}/action_images'
    HEALTH_HEART = cv.imread(f'{ACTION_IMAGES_PATH}/general/health_heart.png', cv.IMREAD_COLOR)
    HEALTH_BAR_FULL = cv.imread(f'{ACTION_IMAGES_PATH}/general/health_bar_full.png', cv.IMREAD_COLOR)
    ADRENALINE_SWORDS = cv.imread(f'{ACTION_IMAGES_PATH}/general/adrenaline_swords.png', cv.IMREAD_COLOR)
    ADRENALINE_BAR_EMPTY = cv.imread(f'{ACTION_IMAGES_PATH}/general/adrenaline_bar_empty.png', cv.IMREAD_COLOR)


    def __init__(self, window_offset, window_size):
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        self.screenshot = None
        self.targets = None
        self.stopped = False

    def update_targets(self, targets):
        self.targets = targets

    def update_screenshot(self, screenshot):
        self.screenshot = screenshot

    def stop(self):
        self.stopped = True

    def heal(self):
        sleep(1.0)
        health_bar_crop = self.locate_bar(self.HEALTH_HEART)
        adrenaline_bar_crop = self.locate_bar(self.ADRENALINE_SWORDS)

        health_match = cv.matchTemplate(health_bar_crop, self.HEALTH_BAR_FULL, cv.TM_CCOEFF_NORMED)
        _, health_max_val, _, _ = cv.minMaxLoc(health_match)

        adrenaline_match = cv.matchTemplate(adrenaline_bar_crop, self.ADRENALINE_BAR_EMPTY, cv.TM_CCOEFF_NORMED)
        _, adrenaline_max_val, _, _ = cv.minMaxLoc(adrenaline_match)

        if health_max_val < 0.9:
            if adrenaline_max_val < 0.5:
                while True:
                    sleep(1.0)
                    adrenaline_bar_crop = self.locate_bar(self.ADRENALINE_SWORDS)
                    adrenaline_match = cv.matchTemplate(adrenaline_bar_crop, self.ADRENALINE_BAR_EMPTY, cv.TM_CCOEFF_NORMED)
                    _, adrenaline_max_val, _, _ = cv.minMaxLoc(adrenaline_match)

                    if adrenaline_max_val >= 0.9:
                        break

        return True

    def locate_bar(self, bar_type):
        result = self.find_item_on_screen(self.screenshot, bar_type, threshold=0.8)
        location_x, location_y = result['location'][0], result['location'][1]
        bar_crop = self.screenshot[location_y-0:location_y+45, location_x+0:location_x+180]
        return bar_crop

    @staticmethod
    def find_item_on_screen(screen_img, item_img, threshold):
        res = cv.matchTemplate(screen_img, item_img, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)

        if max_val >= threshold:
            return {"found": True, "confidence": max_val, "location": max_loc}
        else:
            return {"found": False, "confidence": max_val}
