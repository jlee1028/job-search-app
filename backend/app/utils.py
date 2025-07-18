import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_logger(name):
   logger = logging.getLogger(name)
   logger.setLevel(logging.INFO)
   logger.addHandler(get_console_handler())
   logger.propagate = False
   return logger
