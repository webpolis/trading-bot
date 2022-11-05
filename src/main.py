"""
References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import asyncio
import atexit
import locale
import logging
import sys
import threading

from com.cryptobot.config import Config
from com.cryptobot.extractors.fake_mempool import FakeMempoolExtractor
from com.cryptobot.extractors.mempool import MempoolExtractor
from com.cryptobot.traders.trader import Trader
from com.cryptobot.utils.logger import DebugModuleFilter, PrettyLogger
from com.cryptobot.utils.python import get_class_by_fullname

__author__ = 'Nicolas Iglesias'
__copyright__ = 'Nicolas Iglesias'
__license__ = 'MIT'
__version__ = '0.0.1'
_logger = None

locale.setlocale(locale.LC_ALL, 'en_US.UTF8')

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

settings = Config().get_settings()
threads = []


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description='A multithreaded cryptocurrency bot that reacts to mempool transactions.')
    parser.add_argument(
        '--version',
        action='version',
        version='trading-bot {ver}'.format(ver=__version__),
    )
    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        help='set loglevel to INFO',
        action='store_const',
        const=logging.INFO,
    )
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest='loglevel',
        help='set loglevel to DEBUG',
        action='store_const',
        const=logging.DEBUG,
    )
    parser.add_argument('-d', '--debug_modules',
                        dest='debug_modules', nargs='+', default=[])
    parser.add_argument('-e', '--extractors', help='Overrides enabled extractors in config.json',
                        dest='extractors_override', nargs='+', default=[])
    parser.add_argument('-c', '--classifiers', help='Overrides mempool classifiers in config.json',
                        dest='classifiers_override', nargs='+', default=[])

    return parser.parse_args(args)


def main(args):
    """
    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    global _logger

    args = parse_args(args)
    classifiers_paths = None
    extractors_paths = settings.runtime.extractors.enabled

    if len(args.debug_modules) > 0:
        logging.getLogger(__name__).addFilter(DebugModuleFilter(args.debug_modules))

    if len(args.extractors_override) > 0:
        extractors_paths = args.extractors_override
    if len(args.classifiers_override) > 0:
        classifiers_paths = args.classifiers_override

    _logger = PrettyLogger(__name__, args.loglevel)

    _logger.info('Starting up TradingBot...')

    # init extractors
    for clf in extractors_paths:
        cls = get_class_by_fullname(clf)
        instance = cls() if (
            not issubclass(cls, MempoolExtractor)
            and not issubclass(cls, FakeMempoolExtractor)
        ) else cls(
            classifiers_paths=classifiers_paths)
        thread = threading.Thread(name=clf, daemon=True, target=instance.run)

        threads.append(thread)

    # spawn traders
    if 'com.cryptobot.extractors.mempool.MempoolExtractor' in extractors_paths \
            or 'com.cryptobot.extractors.fake_mempool.FakeMempoolExtractor' in extractors_paths:
        for i in range(0, settings.runtime.traders.max_concurrent_runs):
            asyncio.run(Trader().run())

    # run extractors
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def stop():
    for thread in threads:
        _logger.info(f'Stopping thread {thread.name}')

        thread._stop()


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    atexit.register(stop)

    main(sys.argv[1:])


if __name__ == '__main__':
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m trading_bot.main
    #
    run()
