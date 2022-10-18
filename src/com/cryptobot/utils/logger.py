import logging
import sys
from pprint import pformat


class DebugModuleFilter(logging.Filter):
    def __init__(self, debug_modules):
        logging.Filter.__init__(self)
        self.debug_modules = set(debug_modules)

    def filter(self, record):
        # This filter assumes that we want INFO logging from all
        # modules and DEBUG logging from only selected ones, but
        # easily could be adapted for other policies.
        if record.levelno == logging.DEBUG:
            return record.module in self.debug_modules

        return True


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

    def debug(self, msg, format=False):
        self.logger.debug(msg)
