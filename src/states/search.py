from math import sqrt
from time import sleep

import pyautogui
import cv2 as cv


class SearchState:
    IGNORE_RADIUS = 130
    TOOLTIP_MATCH_THRESHOLD = 0.72

    def __init__(self, object_to_search, window_offset, window_size):
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        self.screenshot = None
        self.targets = None
        self.stopped = False
        #self.click_history = click_history

        self.object_to_search = object_to_search

    def update_targets(self, targets):
        self.targets = targets

    def update_screenshot(self, screenshot):
        self.screenshot = screenshot

    def stop(self):
        self.stopped = True

    def click_next_target(self):
        self.focus()
        targets = self.targets_ordered_by_distance(self.targets)

        target_i = 0
        object_found = False
        while not object_found and target_i < len(targets):
            if self.stopped:
                break

            target_pos = targets[target_i]
            screen_x, screen_y = self.get_screen_position(target_pos)
            print('Moving mouse to x:{} y:{}'.format(screen_x, screen_y))

            # move the mouse
            pyautogui.moveTo(x=screen_x, y=screen_y)
            pyautogui.click(button='right')
            sleep(0.2)


            if self.is_do_action_option_visible():
                print('Click on confirmed target at x:{} y:{}'.format(screen_x, screen_y))
                object_found = True
                pyautogui.click()

                # save this position to the click history
                #self.click_history.append(target_pos)
            target_i += 1

        return object_found

    def focus(self):
        pyautogui.click(x=self.window_offset[0] + (self.window_w // 2), y=self.window_offset[1] + 10)
        sleep(0.2)

    def targets_ordered_by_distance(self, targets):
        my_pos = (self.window_w / 2, self.window_h / 2)

        def pythagorean_distance(pos):
            return sqrt((pos[0] - my_pos[0]) ** 2 + (pos[1] - my_pos[1]) ** 2)

        targets.sort(key=pythagorean_distance)

        # ignore targets at are too close to our character (within 130 pixels) to avoid
        # re-clicking a deposit we just mined
        targets = [t for t in targets if pythagorean_distance(t) > self.IGNORE_RADIUS]

        return targets

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_screen_position(self, pos):
        return pos[0] + self.window_offset[0], pos[1] + self.window_offset[1]

    def is_do_action_option_visible(self):
        do_action_option_path = f'action_images/{self.object_to_search}/do_action_option.png'
        do_action_option = cv.imread(do_action_option_path, cv.IMREAD_COLOR)

        result = cv.matchTemplate(self.screenshot, do_action_option, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
            screen_loc = self.get_screen_position(max_loc)
            tooltip_center_x = screen_loc[0] + (do_action_option.shape[1] // 2)
            tooltip_center_y = screen_loc[1] + (do_action_option.shape[0] // 2)
            pyautogui.moveTo(x=tooltip_center_x, y=tooltip_center_y)
            sleep(0.250)

            return True

        return False