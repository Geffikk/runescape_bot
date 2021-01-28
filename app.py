import os
import argparse
from dotenv import load_dotenv

from src.bot import Bot
from src.mouse_input import MouseInput

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    if sys.argv[1] == "install":
        install("PyAutoGUI")
        install("Pillow")
    exit(0)
except:
    pass

try:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='objective to do or to train bot upon', type=str)
    parser.add_argument('--n_times', help='training clicks amount or bot total loops', type=int)
    parser.add_argument('--action', help='train or run objective', type=str)
    args = parser.parse_args()
except:
    exit(0)

if __name__ == "__main__":
    if args.action == "train":
        MouseInput(args.name, args.n_times)

    elif args.action == "deploy":
        bot = Bot(args.name + ".json", n_loops=args.n_times)
        bot.farm()








