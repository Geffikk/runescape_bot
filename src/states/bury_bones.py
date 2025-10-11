from time import sleep

import pyautogui
import cv2 as cv

from src.states.bot import BotState
from src.states.loot import LootItems
from src.utils.constants import PROJECT_ABSOLUTE_PATH


class BuryBonesState:
    ACTION_IMAGES_PATH = f'{PROJECT_ABSOLUTE_PATH}/action_images'
    BACKPACK_HEADER = cv.imread(f'{ACTION_IMAGES_PATH}/general/backpack_header.png', cv.IMREAD_COLOR)
    BACKPACK_FOOTER = cv.imread(f'{ACTION_IMAGES_PATH}/general/backpack_footer.png', cv.IMREAD_COLOR)


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

    def bury_bones(self):
        inventory_region = self.locate_hud(self.BACKPACK_HEADER, self.BACKPACK_FOOTER)
        i = 0

        while True:
            bones_path = f'{self.ACTION_IMAGES_PATH}/loot/bones.png'
            bones_img = cv.imread(bones_path, cv.IMREAD_COLOR)
            if bones_img is None:
                raise Exception(f"Could not read image file: {bones_path}")

            x, y, w, h = inventory_region
            inventory_img = self.screenshot[y:y + h, x:x + w]

            res = cv.matchTemplate(inventory_img, bones_img, cv.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv.minMaxLoc(res)

            if max_val >= 0.85:
                window_x, window_y = self.compute_icon_center(max_loc, bones_img, (x, y))
                self.pyautogui_move_to_wait_click(window_x, window_y, button='left')
            else:
                break

            i += 1
            sleep(1.0)

        if i > 0:
            return BotState.LOOTING
        else:
            return BotState.SEARCHING

    @staticmethod
    def pyautogui_move_to_wait_click(x, y, button='left'):
        pyautogui.moveTo(x, y)
        sleep(0.2)
        pyautogui.click(button=button)
        sleep(0.2)

    def compute_icon_center(self, location, template, lootbar_offset):
        item_x, item_y = location
        item_h, item_w = template.shape[:2]
        item_cx = item_x + item_w // 2 + lootbar_offset[0]
        item_cy = item_y + item_h // 2 + lootbar_offset[1]
        window_x = self.window_offset[0] + item_cx
        window_y = self.window_offset[1] + item_cy
        return window_x, window_y

    def locate_hud(self, header, footer, threshold=0.8):
        # match header
        res_header = cv.matchTemplate(self.screenshot, header, cv.TM_CCOEFF_NORMED)
        _, max_val_h, _, max_loc_h = cv.minMaxLoc(res_header)
        if max_val_h < threshold:
            raise Exception("Header not found")
        hx, hy = max_loc_h
        hw, hh = header.shape[1], header.shape[0]

        # match footer
        res_footer = cv.matchTemplate(self.screenshot, footer, cv.TM_CCOEFF_NORMED)
        _, max_val_f, _, max_loc_f = cv.minMaxLoc(res_footer)
        if max_val_f < threshold:
            raise Exception("Footer not found")
        fx, fy = max_loc_f
        fw, fh = footer.shape[1], footer.shape[0]

        # region from header top-left to footer bottom
        loot_window_region = (hx, hy, hw, (fy + fh) - hy)
        return loot_window_region
