import random
import time

import cv2
import mss
import numpy as np
import pyautogui
import pytesseract

from src.utils import screen

IMAGES_PATH = '/Users/mgeffert/webdev/runescape_bot/data/images/combat'

SCT = mss.mss()
MONITOR = SCT.monitors[1]


class Combat:
    ARROW_LIST = ['arrow', 'arrows', 'arrows_many']

    def __init__(self, mob=None):
        self.mob = mob
        #self.full_health = self.get_health()

    def farm(self):
        # click on window to focus
        pyautogui.click(x=MONITOR["left"] + (MONITOR["width"] // 2), y=MONITOR["top"] + (MONITOR["height"] // 2))

        mob_counter = 0
        pickup_on = random.uniform(2, 4)
        replenish_health = False
        while True:
            moving_objects_cords = self.locate_moving_objects()

            for moving_object_cords in moving_objects_cords:
                x, y = moving_object_cords
                pyautogui.moveTo(x, y)

                #mob_cords = self.find_color_in_screen()
                #mob_name = screen.locate_on_screen(f'{IMAGES_PATH}/mob.png', confidence=0.6)
                attack_box = screen.locate_center_on_screen(f'{IMAGES_PATH}/locate_minotaur.png', confidence=0.8)

                if attack_box:
                    pyautogui.click(button='right')
                    attack_box = screen.locate_center_on_screen(f'{IMAGES_PATH}/attack_minotaur.png', confidence=0.8)

                    if attack_box:
                        pyautogui.moveTo(attack_box)
                        pyautogui.click(button='left')
                        time.sleep(random.uniform(1.0, 1.3))

                        stack_value = screen.locate_center_on_screen(f'{IMAGES_PATH}/locked_mob.png', confidence=0.80)
                        if stack_value:
                            replenish_health = self.replenish_health()

                            while True:
                                stack_value = screen.locate_center_on_screen(f'{IMAGES_PATH}/locked_mob.png', confidence=0.80)

                                if stack_value is None:
                                    break

                                time.sleep(0.5)

                            break

            time.sleep(random.lognormvariate(0.4, 0.2))
            self.loot_arrows(['adamant', 'iron'])

            if replenish_health:
                pass
                #food = screen.locate_center_on_screen(f'{IMAGES_PATH}/cooked_meat.png', confidence=0.70)
                #pyautogui.moveTo(food)
                #pyautogui.click(button='left')
                #time.sleep(random.uniform(0.5, 1.0))
                #replenish_health = False

            mob_counter += 1
            if mob_counter % pickup_on == 0:
                self.loot_items(['bones'])
                self.bury_bones()


            #print("a")


    @classmethod
    def replenish_health(cls):
        health_bar = screen.locate_on_screen(f'{IMAGES_PATH}/health_bar.png', confidence=0.6)

        if health_bar:
            return False

        return True

    @classmethod
    def is_inventory_full(cls):
        inventory_full = screen.locate_on_screen(f'{IMAGES_PATH}/not_full_inventory.png', confidence=0.9)
        return False if inventory_full else True

    def bury_bones(self):
        inventory_region = self.locate_inventory_region()

        while True:
            bones = screen.locate_center_on_screen(f'{IMAGES_PATH}/bones.png', confidence=0.95, region=inventory_region)

            if bones:
                pyautogui.moveTo(bones)
                pyautogui.click(button='left')
            else:
                break

            time.sleep(random.uniform(0.5, 1))

    @classmethod
    def locate_inventory_region(cls):
        inventory_header = screen.locate_on_screen(f'{IMAGES_PATH}/inventory_header.png', confidence=0.8)
        inventory_footer = screen.locate_on_screen(f'{IMAGES_PATH}/inventory_footer.png', confidence=0.8)
        inventory_region = (inventory_header[0], inventory_header[1], inventory_header.width, inventory_footer[1] - inventory_header[1])

        return inventory_region

    def loot_arrows(self, arrow_types):
        loot_window_region = self.locate_loot_window_region()

        for arrow in self.ARROW_LIST:
            while True:
                arrow_location = screen.locate_center_on_screen(f'{IMAGES_PATH}/{arrow}.png', confidence=0.75, region=loot_window_region)

                if arrow_location:
                    pyautogui.moveTo(arrow_location)
                    pyautogui.click(button='right')

                    for arrow_type in arrow_types:
                        arrow_type = screen.locate_center_on_screen(f'{IMAGES_PATH}/arrow_{arrow_type}.png', confidence=0.75)
                        if arrow_type:
                            pyautogui.moveTo(arrow_type)
                            pyautogui.click(button='left')
                            time.sleep(random.lognormvariate(0.3, 0.2))
                            break
                else:
                    break

    def loot_items(self, items):
        items = sorted(items, key=lambda x: 0 if 'arrow' in x else 1)
        loot_window_region = self.locate_loot_window_region()

        for item in items:
            while True:
                if self.is_inventory_full():
                    return

                item_path = f'{IMAGES_PATH}/{item}.png'
                item_location = screen.locate_center_on_screen(item_path, confidence=0.80, region=loot_window_region)

                if item_location:
                    pyautogui.moveTo(item_location)
                    pyautogui.click(button='left')
                    time.sleep(random.lognormvariate(0.3, 0.2))
                else:
                    break

                time.sleep(random.uniform(0.5, 1))


    @classmethod
    def locate_loot_window_region(cls):
        loot_window_header = screen.locate_on_screen(f'{IMAGES_PATH}/loot_window_header.png', confidence=0.8)
        loot_window_footer = screen.locate_on_screen(f'{IMAGES_PATH}/loot_window_footer.png', confidence=0.8)

        if not loot_window_header or not loot_window_footer:
            raise Exception('Could not locate loot window region')

        loot_window_region = (loot_window_header[0], loot_window_header[1], loot_window_header.width, loot_window_footer[1] - loot_window_header[1])
        return loot_window_region

    @classmethod
    def locate_moving_objects(cls):
        # Capture the first frame from the screen
        screenshot1 = np.array(SCT.grab(MONITOR))
        screenshot1 = cv2.cvtColor(screenshot1, cv2.COLOR_BGR2GRAY)
        screenshot1 = cv2.GaussianBlur(screenshot1, (21, 21), 0)

        time.sleep(0.1)

        # Capture the second frame from the screen
        screenshot2 = np.array(SCT.grab(MONITOR))
        screenshot2 = cv2.cvtColor(screenshot2, cv2.COLOR_BGR2GRAY)
        screenshot2 = cv2.GaussianBlur(screenshot2, (21, 21), 0)

        diff = cv2.absdiff(screenshot1, screenshot2)

        # Threshold the difference to get the regions of motion
        _, thresh = cv2.threshold(diff, 1, 255, cv2.THRESH_BINARY)

        # Find contours of the moving areas
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        objects = []
        for contour in contours:
            print(cv2.contourArea(contour))
            if cv2.contourArea(contour) < 500:
                continue
            x, y, w, h = cv2.boundingRect(contour)

            # Map the bounding box to the original screen coordinates
            x_center = x + MONITOR["left"] + w // 2
            y_center = y + MONITOR["top"] + h // 2

            if w > 50 and h > 50:
                objects.append((x_center, y_center))

        return objects

    @classmethod
    def capture_screen(cls):
        """Capture the screen using mss"""
        with mss.mss() as sct:
            # Capture the screen (monitor 1)
            screenshot = np.array(sct.grab(MONITOR))
            cv2.imwrite('screenshot.png', screenshot)
            return screenshot

    def find_color_in_screen(self):
        bgr_color = np.array([255, 0, 255])  # Lower bound for purple

        # Convert the provided BGR color to HSV
        bgr_color_np = np.uint8([[bgr_color]])  # Convert the BGR color to NumPy array
        hsv_color = cv2.cvtColor(bgr_color_np, cv2.COLOR_BGR2HSV)[0][0]

        # Define a range around the color (tolerance can be adjusted)
        lower_color = np.array([hsv_color[0] - 10, 100, 100])  # Adjust hue range
        upper_color = np.array([hsv_color[0] + 10, 255, 255])

        """Find the specified color on the screen"""
        # Capture the screen
        screen_img = self.capture_screen()

        # Convert the image to HSV for better color detection
        hsv_image = cv2.cvtColor(screen_img, cv2.COLOR_BGR2HSV)

        cv2.imwrite('hsv_image.png', hsv_image)

        # Create a mask for the desired color range
        mask = cv2.inRange(hsv_image, lower_color, upper_color)

        # Find contours of the masked area
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # If contours are found, return the bounding box of the first one
        if contours:
            # filter h < 50 and w < 50
            contours = [contour for contour in contours if cv2.boundingRect(contour)[2] > 30 and cv2.boundingRect(contour)[3] > 30]

            x, y, w, h = cv2.boundingRect(contours[0])
            return (x + 10, y + 5, w, h)
        else:
            return None
