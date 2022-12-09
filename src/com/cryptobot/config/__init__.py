
import sys

from com.cryptobot.utils.path import get_project_root
from python_json_config import ConfigBuilder

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import (PackageNotFoundError,  # pragma: no cover
                                    version)
else:
    from importlib_metadata import (PackageNotFoundError,  # pragma: no cover
                                    version)

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "trading-bot"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


class Config:
    def __init__(self):
        self.builder = ConfigBuilder()
        self.params_file = 'config.json'

    def init_settings(self, file='config.json'):
        self.params_file = file

    def get_settings(self):
        return self.builder.parse_config(get_project_root() + f'/{self.params_file}')
