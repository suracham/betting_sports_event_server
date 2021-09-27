import logging
from logging.handlers import *

def get_logger(owner, logfile, loglevel=logging.DEBUG):
  logger = logging.getLogger(owner)
  logger.setLevel(logging.DEBUG)
  # create formatter
  formatter = logging.Formatter('%(asctime)s' + ' - %(message)s')

  if logfile:
    h = WatchedFileHandler(logfile)
    h.setFormatter(formatter)
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)

  # create console handler and set level to debug
  h = logging.StreamHandler()
  h.setLevel(loglevel)
  h.setFormatter(formatter)
  logger.addHandler(h)

  return logger

def stop_logger(logger):
    for handler in logger.handlers :
        logger.removeHandler(handler)

    if len(logger.handlers) > 0:
       logger.removeHandler(logger.handlers[0])
