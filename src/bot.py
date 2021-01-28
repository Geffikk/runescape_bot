import json
import os
import time
import random

import pyautogui

from src.mouse_output import MouseOutput


class Bot:
    def __init__(self,  objective, n_loops):
        self.objective = objective
        self.n_loops = n_loops
        self.current_loops = 0
        self.objective_path = self._load_objective()
        self.mouse = MouseOutput()

    """ 
        Deserialize JSON mouse input paths

        Returns:
            list: list of point objects
        
    """
    def _load_objective(self):
        data = os.path.join(os.getenv('DATA_DIR'), os.getenv('OBJECTIVE_DIR'), self.objective)
        with open(data, "r") as file:
            brain = file.read()
            return json.loads(brain)

    """  Iterates N times from specified loop count an then iterates n times over action path to control the bot  """

    def loop(self):

        while self.current_loops < self.n_loops:
            for idx, action in enumerate(self.objective_path):
                x, y, button, _time = action['x'], action['y'], action['button'], action['time']
                try:
                    next_action_time = self.objective_path[idx + 1]['time']
                    pause_time = next_action_time - _time
                except IndexError as e:
                    pause_time = 0

                self.mouse.set_mouse_position(x+random.uniform(-5.0, 5.0), y+random.uniform(-5.0, 5.0))
                time.sleep(0.2)
                self.mouse.click(button)
                time.sleep(pause_time)

            self.current_loops +=1

    def farm(self):

        while self.current_loops < self.n_loops:
            first = True
            for idx, action in enumerate(self.objective_path):
                x, y, button, _time = action['x'], action['y'], action['button'], action['time']
                try:
                    next_action_time = self.objective_path[idx + 1]['time']
                    pause_time = next_action_time - _time
                except IndexError as e:
                    pause_time = 0

                self.mouse.set_mouse_position(x+random.uniform(-5.0, 5.0), y+random.uniform(-5.0, 5.0))
                time.sleep(0.2)
                self.mouse.click(button)

                if first:
                    first = False
                    while True:
                        try:
                            last_slot = pyautogui.locateCenterOnScreen('D:\\GitHub\\runescape-bot\\last_slot.png')
                            if last_slot is None:
                                break
                        except:
                            break
                        time.sleep(1)
                else:
                    time.sleep(pause_time)

            self.current_loops += 1
