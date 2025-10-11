import logging
import os

LOGGING_LEVEL = logging.INFO

nested_script_directory = os.path.dirname(os.path.realpath(__file__))
nested_script_directory = os.path.dirname(nested_script_directory)
PROJECT_ABSOLUTE_PATH = os.path.dirname(nested_script_directory)