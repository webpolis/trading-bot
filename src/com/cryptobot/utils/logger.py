import logging
import sys
from pprint import pformat


class PrettyLogger():
    def __init__(self, name: str, loglevel=logging.DEBUG):
        self.logger = logging.getLogger(name)
        logformat = '[%(asctime)s] %(levelname)s:%(name)s:%(message)s'

        logging.basicConfig(
            level=loglevel, stream=sys.stdout, format=logformat, datefmt='%Y-%m-%d %H:%M:%S'
        )

    def info(self, msg, format=False):
        if format:
            self.logger.info('\n%s', pformat(msg, indent=1, width=1))
        else:
            self.logger.info(msg)

    def error(self, msg, format=False):
        self.logger.error(msg)
