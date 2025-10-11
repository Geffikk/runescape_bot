import yaml

from src.utils.constants import PROJECT_ABSOLUTE_PATH

with open(f'{PROJECT_ABSOLUTE_PATH}/config/loot_items.yaml', "r") as f:
    loot_data = yaml.safe_load(f)