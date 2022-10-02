import logging
import sys

def get_logger(name: str, loglevel=logging.DEBUG):
    logger = logging.getLogger(name)
    logformat = '[%(asctime)s] %(levelname)s:%(name)s:%(message)s'

    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt='%Y-%m-%d %H:%M:%S'
    )

    return logger
