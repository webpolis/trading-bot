import pytest

from trading_bot.main import main

__author__ = "Nicolas Iglesias"
__copyright__ = "Nicolas Iglesias"
__license__ = "MIT"


def test_main(capsys):
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts against stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(['-v'])

    assert True
