"""
References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys
import threading

from com.cryptobot.extractors.accounts import AccountsExtractor
from com.cryptobot.extractors.mempool import MempoolExtractor
from com.cryptobot.utils.logger import get_logger

__author__ = 'Nicolas Iglesias'
__copyright__ = 'Nicolas Iglesias'
__license__ = 'MIT'
__version__ = '0.0.1'
_logger = None

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description='A crypto trading bot')
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

    return parser.parse_args(args)


def main(args):
    """
    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    global _logger

    args = parse_args(args)
    _logger = get_logger(__name__, args.loglevel)

    _logger.info('Starting up TradingBot...')

    # init extractors
    ae_thread = threading.Thread(name='AccountsExtractor',
                                 daemon=True, target=AccountsExtractor().run)
    mp_thread = threading.Thread(name='MempoolExtractor',
                                 daemon=True, target=MempoolExtractor().run)

    # run extractors
    # ae_thread.start()
    mp_thread.start()

    # ae_thread.join()
    mp_thread.join()


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
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
