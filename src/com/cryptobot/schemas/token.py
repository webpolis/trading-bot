import json
import logging
from enum import Enum

from com.cryptobot.config import Config
from com.cryptobot.schemas.schema import Schema
from com.cryptobot.utils.alchemy import api_post
from com.cryptobot.utils.coingecko import get_coin, is_stablecoin
from com.cryptobot.utils.network import ProviderNetwork, get_current_network, is_eth_address
from com.cryptobot.utils.ethplorer import get_token_info
from com.cryptobot.utils.explorer import get_token_info as get_xp_token_info
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.pandas_utils import get_token_by_address
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.redis_mixin import RedisMixin
from toolz import valfilter

settings = Config().get_settings()
alchemy_api_keys = iter(settings.web3.providers.alchemy.api_keys)

# initialize data
with open(get_data_path() + 'ftx_coins.json') as f:
    ftx_coins = json.load(f)

    f.close()


class TokenSource(Enum):
    COINGECKO = 1
    FTX = 2
    FTX_LENDING = 3
    ETHPLORER = 4
    COINMARKETCAP = 5


class Token(Schema, RedisMixin):
    cached_alchemy_metadata = {}
    cached_ethplorer_metadata = {}
    cached_explorer_metadata = {}

    def __init__(self, symbol=None, name=None, market_cap=None, price_usd=None, address=None, decimals=None, no_live_checkup=False):
        self._logger = PrettyLogger(__name__, logging.INFO)
        self.address = address.lower() if type(address) == str else address
        self.symbol = symbol.upper() if type(symbol) == str else symbol
        self.name = name
        self.market_cap = float(
            market_cap) if market_cap != None else self.get('market_cap')
        self.price_usd = float(
            price_usd) if price_usd != None else self.get('price_usd')
        self.decimals = decimals
        self._alchemy_metadata = None
        self._ethplorer_metadata = None
        self._explorer_metadata = None
        self._metadata = None
        self.no_live_checkup = no_live_checkup

        if self.no_live_checkup:
            return

        # populate missing data
        self._metadata = self.metadata()

        if self._metadata is not None:
            if self.symbol is None:
                self.symbol = self._metadata.get('symbol', None).upper()

            if self.name is None:
                self.name = self._metadata.get('name', None)

            if self.market_cap is None:
                self.market_cap = float(self._metadata.get('market_cap', 0))

            if self.decimals is None:
                self.decimals = int(self._metadata.get('decimals', 18))

            if self.price_usd is None:
                self.price_usd = float(self._metadata.get('price_usd', 0))

            if self.address is None:
                self.address = self._metadata.get('address', None)

        # populate ERC20 address
        if self.address is None:
            # 1st try
            if self._coingecko_coin != None:
                self.address = self._coingecko_coin['platforms']['ethereum'].lower() if \
                    self._coingecko_coin['platforms'].get(
                    'ethereum', None) != None else None

            # 2nd try
            if self.address is None:
                if self._ftx_coin != None:
                    self.address = self._ftx_coin['erc20Contract'].lower()

        if self.address == '':
            self.address = None

        if self.price_usd is None:
            self.price_usd = float(self._ftx_coin.get(
                'indexPrice', 0)) if self._ftx_coin is not None else None

        if self.price_usd != None:
            self.set('price_usd', self.price_usd,
                     ttl=settings.runtime.schemas.token.price_usd_ttl)

        if self.market_cap != None:
            self.set('market_cap', self.market_cap,
                     ttl=settings.runtime.schemas.token.market_cap_ttl)

    @property
    def __key__(self):
        return (self.symbol, self.address)

    @property
    def _coingecko_coin(self):
        return get_coin(self.symbol)

    @property
    def _ftx_coin(self):
        return next(iter([coin for coin in ftx_coins if coin['id'].upper() == self.symbol
                          and coin.get('erc20Contract', None) != None]), None)

    @property
    def stablecoin(self):
        return is_stablecoin(self.symbol)

    def from_dict(dict_obj={}, address=None):
        dict_obj = {} if dict_obj == None else dict_obj
        network = get_current_network()

        # map network's token address
        address = dict_obj.get('address', address)

        if network == ProviderNetwork.ARBITRUM:
            address = dict_obj.get('address_arbitrum', address)
        elif network == ProviderNetwork.POLYGON:
            address = dict_obj.get('address_polygon', address)

        return Token(dict_obj.get('symbol', None),
                     dict_obj.get('name', None),
                     dict_obj.get('market_cap', None),
                     dict_obj.get('price_usd', None),
                     address)

    def metadata(self) -> dict:
        """Populate token with all the data we can gather from many different sources"""
        _cached_metadata = self.get('metadata')
        self._metadata = None if _cached_metadata is None else _cached_metadata

        if self._metadata != None:
            return self._metadata

        mixed_metadata = {}

        # fetch data collected by the TokensExtractor
        self._metadata = get_token_by_address(self.address)

        # start fetching from other sources
        _explorer_metadata = None
        _alchemy_metadata = self.fetch_alchemy_metadata()
        _ethplorer_metadata = self.fetch_ethplorer_metadata()
        _explorer_metadata = self.fetch_explorer_metadata(metadata=self._metadata)

        # combine all the data
        if self._metadata is not None:
            mixed_metadata = {**mixed_metadata, **self._metadata}

        if _alchemy_metadata is not None:
            mixed_metadata = {**mixed_metadata, **_alchemy_metadata}

        if _ethplorer_metadata is not None:
            mixed_metadata = {**mixed_metadata, **_ethplorer_metadata}

        if _explorer_metadata is not None:
            mixed_metadata = {**mixed_metadata, **_explorer_metadata}

        self._metadata = valfilter(lambda v: v != None, mixed_metadata)

        # cache the metadata
        if self._metadata != None and len(self._metadata) > 0:
            self.set('metadata', self._metadata,
                     ttl=settings.runtime.schemas.token.metadata_ttl)

        return self._metadata

    def fetch_explorer_metadata(self, metadata=None) -> dict:
        # we don't need anything extra than these attributes
        if (self.price_usd != None and self.market_cap != None and self.address != None):
            return {}

        has_local_metadata = self._explorer_metadata is not None
        has_cached_metadata = self.address in Token.cached_explorer_metadata

        if has_local_metadata:
            return self._explorer_metadata

        if has_cached_metadata:
            return Token.cached_explorer_metadata[self.address]

        try:
            response = get_xp_token_info(self.address)
            _explorer_metadata = valfilter(
                lambda v: v != None, response if type(response) == dict else dict())

            if len(_explorer_metadata) > 0:
                self._explorer_metadata = _explorer_metadata
                Token.cached_explorer_metadata[self.address] = self._explorer_metadata
        except Exception as error:
            self._logger.error({'error': error.with_traceback(), 'token': str(self)})
        finally:
            return self._explorer_metadata

    def fetch_ethplorer_metadata(self) -> dict:
        # we don't need anything extra than these attributes
        if (self.price_usd != None and self.market_cap != None and self.address != None):
            return {}

        has_local_metadata = self._ethplorer_metadata is not None
        has_cached_metadata = self.address in Token.cached_ethplorer_metadata

        if has_local_metadata:
            return self._ethplorer_metadata

        if has_cached_metadata:
            return Token.cached_ethplorer_metadata[self.address]

        try:
            response = get_token_info(self)
            _ethplorer_metadata = valfilter(
                lambda v: v != None, response if type(response) == dict else dict())

            if len(_ethplorer_metadata) > 0:
                self._ethplorer_metadata = _ethplorer_metadata
                Token.cached_ethplorer_metadata[self.address] = self._ethplorer_metadata
        except Exception as error:
            self._logger.error({'error': error.with_traceback(), 'token': str(self)})
        finally:
            return self._ethplorer_metadata

    def fetch_alchemy_metadata(self) -> dict:
        # only useful thing provided here is decimals
        if self.decimals != None or (self.address is None or is_eth_address(self.address)):
            return {}

        has_local_metadata = self._alchemy_metadata is not None
        has_cached_metadata = self.address in Token.cached_alchemy_metadata

        if has_local_metadata:
            return self._alchemy_metadata

        if has_cached_metadata:
            return Token.cached_alchemy_metadata[self.address]

        payload = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'alchemy_getTokenMetadata',
            'params': [self.address]
        }

        try:
            response = api_post(payload)
            _alchemy_metadata = valfilter(
                lambda v: v != None, response.get('result', {}))

            if len(_alchemy_metadata) > 0:
                self._alchemy_metadata = _alchemy_metadata
                Token.cached_alchemy_metadata[self.address] = self._alchemy_metadata
        except Exception as error:
            self._logger.error({'error': error, 'token': str(self)})
        finally:
            return self._alchemy_metadata

    def __str__(self):
        return str(self.__dict__)

    @property
    def __dict__(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'address': self.address,
            'market_cap': self.market_cap,
            'price_usd': self.price_usd,
            'decimals': self.decimals
        }
