import random
from enum import Enum
from time import sleep

import pyautogui
import cv2 as cv
import logging

from src.states.bot import BotState
from src.utils.constants import PROJECT_ABSOLUTE_PATH, LOGGING_LEVEL
from src.utils.files import loot_data


logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_LEVEL)

class LootItems(Enum):
    COIN = loot_data["COIN"]
    ARROWS = loot_data["ARROWS"]
    BONES  = loot_data["BONES"]
    FIRE_RUNE = loot_data["FIRE_RUNE"]
    LAW_RUNE = loot_data["LAW_RUNE"]
    WATER_RUNE = loot_data["WATER_RUNE"]

    @property
    def type(self):
        return self.value["type"] if "type" in self.value else None

    @property
    def img_representations(self):
        return self.value["img_representations"] if "img_representations" in self.value else None

    @property
    def values(self):
        return self.value["value"] if "value" in self.value else None


class LootState:
    ACTION_IMAGES_PATH = f'{PROJECT_ABSOLUTE_PATH}/action_images'
    EMPTY_SLOT = cv.imread(f'{ACTION_IMAGES_PATH}/general/empty_slot.png', cv.IMREAD_COLOR)
    LOOTBAR_HEADER = cv.imread(f'{ACTION_IMAGES_PATH}/general/lootbar_header.png', cv.IMREAD_COLOR)
    LOOTBAR_FOOTER = cv.imread(f'{ACTION_IMAGES_PATH}/general/lootbar_footer.png', cv.IMREAD_COLOR)
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

    def loot_items(self, items):
        sleep(0.5)  # wait a second to let the loot appear
        # shuffle items to loot arrows first (since they stack)
        #random.shuffle(items)

        for item in items:
            while True:
                if self.is_inventory_full():
                    return BotState.BURY_BONES

                if self.is_stacked_item(item):
                    self.loot_stacking_items(item)
                    break  # break the while True loop and continue with the next item
                else:
                    looted = self.loot_non_stacking_items(item)
                    if not looted:
                        break  # break the while True loop and continue with the next item

        return BotState.SEARCHING


    def loot_non_stacking_items(self, item: LootItems):
        lootbar_coordinates = self.locate_hud(self.LOOTBAR_HEADER, self.LOOTBAR_FOOTER)

        lootbar_x, lootbar_y, lootbar_w, lootbar_h = lootbar_coordinates
        lootbarshot = self.screenshot[lootbar_y:lootbar_y + lootbar_h, lootbar_x:lootbar_x + lootbar_w]

        item_value_path = f"{self.ACTION_IMAGES_PATH}/loot/{item.value}.png"
        item_template = cv.imread(item_value_path, cv.IMREAD_COLOR)
        if item_template is None:
            return False

        res = cv.matchTemplate(lootbarshot, item_template, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        logger.warning(f"Loot item {item.value} is visible with match confidence: {max_val}")

        if max_val >= 0.75:
            window_x, window_y = self.compute_icon_center(max_loc, item_template, (lootbar_x, lootbar_y))
            self.pyautogui_move_to_wait_click(window_x, window_y, button='left')
            return True  # successfully looted the item

        sleep(0.2)
        return False


    def loot_stacking_items(self, item):
        lootbar_coordinates = self.locate_hud(self.LOOTBAR_HEADER, self.LOOTBAR_FOOTER)
        lootbar_x, lootbar_y, lootbar_w, lootbar_h = lootbar_coordinates

        img_representations = item.img_representations
        img_representations = [f'{self.ACTION_IMAGES_PATH}/loot/{img}.png' for img in img_representations]

        for item_value in item.values:
            item_value_path = f"{self.ACTION_IMAGES_PATH}/loot/take_{item_value}.png"
            item_value_img = cv.imread(item_value_path, cv.IMREAD_COLOR)
            if item_value_img is None:
                continue

            # crop wider region for text detection
            lootbarshot = self.screenshot[lootbar_y:lootbar_y + lootbar_h, lootbar_x - 5:lootbar_x + lootbar_w + 30]

            # found menu text → now try each representation for the base icon
            for img in img_representations:
                arrow_template = cv.imread(img, cv.IMREAD_COLOR)
                if arrow_template is None:
                    continue

                result = self.find_item_on_screen(lootbarshot, arrow_template, 0.6)
                logger.warning(f"Loot template: {img} is visible with match confidence: {result}")
                if not result["found"]:
                    continue

                window_x, window_y = self.compute_icon_center(result["location"], arrow_template, (lootbar_x, lootbar_y))
                self.pyautogui_move_to_wait_click(window_x, window_y, button='right')

                lootbarshot = self.screenshot[lootbar_y:lootbar_y + lootbar_h, lootbar_x - 5:lootbar_x + lootbar_w + 30]
                value_result = self.find_item_on_screen(lootbarshot, item_value_img, 0.75)
                logger.warning(f"Loot item {item_value} is visible with match confidence: {value_result['confidence']}")
                if not value_result["found"]:
                    continue

                window_x, window_y = self.compute_icon_center(value_result["location"], item_value_img, (lootbar_x - 5, lootbar_y))
                self.pyautogui_move_to_wait_click(window_x, window_y, button='left')
                sleep(0.3)
                break  # break inner loop (stop checking other images once looted)

    @staticmethod
    def pyautogui_move_to_wait_click(x, y, button):
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

    @staticmethod
    def find_item_on_screen(screen_img, item_img, threshold):
        res = cv.matchTemplate(screen_img, item_img, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)

        if max_val >= threshold:
            return {"found": True, "confidence": max_val, "location": max_loc}
        else:
            return {"found": False, "confidence": max_val}

    @staticmethod
    def is_stacked_item(item: LootItems):
        if item.img_representations is not None and len(item.img_representations) > 0:
            return True
        return False

    def is_inventory_full(self):
        backpack_coordinates = self.locate_hud(self.BACKPACK_HEADER, self.BACKPACK_FOOTER)
        x, y, w, h = backpack_coordinates
        backpackshot = self.screenshot[y:y + h, x:x + w]

        res = cv.matchTemplate(backpackshot, self.EMPTY_SLOT, cv.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv.minMaxLoc(res)
        logger.warning(f'Inventory empty slot match confidence: {max_val}')

        if max_val > 0.4:
            return False
        else:
            return True

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
