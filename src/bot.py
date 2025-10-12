import random

import cv2 as cv
import numpy as np
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from math import sqrt

from src.states.bot import BotState
from src.states.bury_bones import BuryBonesState
from src.states.fight import FightState
from src.states.heal import HealState
from src.states.loot import LootState, LootItems
from src.states.search import SearchState


class AlbionBot:
    # constants
    INITIALIZING_SECONDS = 5
    MINING_SECONDS = 14
    MOVEMENT_STOPPED_THRESHOLD = 0.975
    IGNORE_RADIUS = 130
    TOOLTIP_MATCH_THRESHOLD = 0.72
    LOCKED_MOB_TOOLTIP = 0.90

    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    limestone_tooltip = None
    click_history = []

    bot_context = None

    def __init__(self, window_offset, window_size):
        # create a thread lock object
        self.lock = Lock()

        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()

        self.search_state = SearchState('catablepon', self.window_offset, window_size)
        self.fight_state = FightState(self.window_offset, window_size)
        self.loot_state = LootState(self.window_offset, window_size)
        self.bury_bones_state = BuryBonesState(self.window_offset, window_size)
        self.heal_state = HealState(self.window_offset, window_size)

    # threading methods
    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.search_state.update_targets(self.targets)
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.search_state.update_screenshot(self.screenshot)
        self.fight_state.update_screenshot(self.screenshot)
        self.loot_state.update_screenshot(self.screenshot)
        self.bury_bones_state.update_screenshot(self.screenshot)
        self.heal_state.update_screenshot(self.screenshot)
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.lock.acquire()
        self.stopped = True
        self.search_state.stop()
        self.fight_state.stop()
        self.loot_state.stop()
        self.bury_bones_state.stop()
        self.heal_state.stop()
        self.lock.release()

    def have_stopped_moving(self):
        # if we haven't stored a screenshot to compare to, do that first
        if self.movement_screenshot is None:
            self.movement_screenshot = self.screenshot.copy()
            return False

        # compare the old screenshot to the new screenshot
        result = cv.matchTemplate(self.screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        # we only care about the value when the two screenshots are laid perfectly over one
        # another, so the needle position is (0, 0). since both images are the same size, this
        # should be the only result that exists anyway
        similarity = result[0][0]
        print('Movement detection similarity: {}'.format(similarity))

        if similarity >= self.MOVEMENT_STOPPED_THRESHOLD:
            # pictures look similar, so we've probably stopped moving
            print('Movement detected stop')
            return True

        # looks like we're still moving.
        # use this new screenshot to compare to the next one
        self.movement_screenshot = self.screenshot.copy()
        return False

    def set_safe_state(self, state):
        self.lock.acquire()
        self.state = state
        self.lock.release()

    def click_backtrack(self):
        # pop the top item off the clicked points stack. this will be the click that
        # brought us to our current location.
        last_click = self.click_history.pop()
        # to undo this click, we must mirror it across the center point. so if our
        # character is at the middle of the screen at ex. (100, 100), and our last
        # click was at (120, 120), then to undo this we must now click at (80, 80).
        # our character is always in the center of the screen
        my_pos = (self.window_w / 2, self.window_h / 2)
        mirrored_click_x = my_pos[0] - (last_click[0] - my_pos[0])
        mirrored_click_y = my_pos[1] - (last_click[1] - my_pos[1])
        # convert this screenshot position to a screen position
        screen_x, screen_y = self.get_screen_position((mirrored_click_x, mirrored_click_y))
        print('Backtracking to x:{} y:{}'.format(screen_x, screen_y))
        pyautogui.moveTo(x=screen_x, y=screen_y)
        # short pause to let the mouse movement complete
        sleep(0.500)
        pyautogui.click()

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])


    # main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    #self.state = BotState.HEALING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                success = self.search_state.click_next_target()

                if success:
                    self.set_safe_state(BotState.FIGHTING)

            elif self.state == BotState.FIGHTING:
                is_fighting = self.fight_state.still_fighting()

                if is_fighting:
                    # still fighting
                    sleep(1.0)
                else:
                    self.set_safe_state(BotState.LOOTING)

            elif self.state == BotState.LOOTING:
                next_state = self.loot_state.loot_items([LootItems.BONES, LootItems.ARROWS, LootItems.FIRE_RUNE, LootItems.WATER_RUNE, LootItems.LAW_RUNE, LootItems.COIN])

                if next_state == BotState.BURY_BONES:
                    self.set_safe_state(BotState.BURY_BONES)
                elif next_state == BotState.SEARCHING:
                    self.set_safe_state(BotState.SEARCHING)

            elif self.state == BotState.BURY_BONES:
                next_state = self.bury_bones_state.bury_bones()
                if next_state == BotState.LOOTING:
                    self.set_safe_state(BotState.LOOTING)
                elif next_state == BotState.SEARCHING:
                    self.set_safe_state(BotState.SEARCHING)
            elif self.state == BotState.HEALING:
                self.heal_state.heal()
                self.set_safe_state(BotState.SEARCHING)

