import json
from enum import Enum

from com.cryptobot.config import Config
from com.cryptobot.schemas.schema import Schema
from com.cryptobot.utils.coingecko import get_price
from com.cryptobot.utils.ethplorer import get_token_info
from com.cryptobot.utils.pandas_utils import get_token_by_address
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.redis_mixin import RedisMixin
from com.cryptobot.utils.alchemy import api_post
from toolz import valfilter

settings = Config().get_settings()
alchemy_api_keys = iter(settings.web3.providers.alchemy.api_keys)

# initialize data
with open(get_data_path() + 'coingecko_coins.json') as f:
    cg_coins = json.load(f)

    f.close()

with open(get_data_path() + 'ftx_coins.json') as f:
    ftx_coins = json.load(f)

    f.close()


class TokenSource(Enum):
    COINGECKO = 1
    FTX = 2
    FTX_LENDING = 3
    ETHPLORER = 4


class Token(Schema, RedisMixin):
    working_api_key = None
    cached_alchemy_metadata = {}
    cached_ethplorer_metadata = {}

    def __init__(self, symbol=None, name=None, market_cap=None, price_usd=None, address=None, decimals=None, no_price_checkup=False):
        self.symbol = symbol.upper() if type(symbol) == str else symbol
        self.name = name
        self.market_cap = market_cap
        self.address = address.lower() if type(address) == str else address
        self.price_usd = price_usd if type(
            price_usd) == float else self.get('price_usd')
        self.decimals = decimals
        self._alchemy_metadata = None
        self._ethplorer_metadata = None
        self._metadata = self.metadata()
        self.no_price_checkup = no_price_checkup

        # populate missing data
        if self._metadata is not None:
            if self.symbol is None:
                self.symbol = self._metadata.get('symbol', None)

            if self.name is None:
                self.name = self._metadata.get('name', None)

            if self.market_cap is None:
                self.market_cap = self._metadata.get('market_cap', None)

            if self.decimals is None:
                self.decimals = int(self._metadata.get('decimals', 18))

            if self.price_usd is None:
                self.price_usd = self._metadata.get('price_usd', None)

            if self.address is None:
                self.address = self._metadata.get('address', None)

        self._coingecko_coin = next(iter([coin for coin in cg_coins if
                                          coin['symbol'].upper() == self.symbol]), None)
        self._ftx_coin = next(iter([coin for coin in ftx_coins if coin['id'].upper() == self.symbol
                                    and coin.get('erc20Contract', None) != None]), None)

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

        if self.price_usd is None:
            self.price_usd = self._ftx_coin['indexPrice'] if self._ftx_coin is not None else None

        # fetch price from coingecko
        if not self.no_price_checkup and self.price_usd is None and self._coingecko_coin is not None:
            try:
                self.price_usd = get_price(self._coingecko_coin['id'], 'usd')
            except Exception as error:
                print({'error': error, 'token': str(self)})

        # @TODO: fetch price from coinmarketcap

        if self.price_usd != None:
            self.set('price_usd', self.price_usd,
                     ttl=settings.runtime.schemas.token.price_usd_ttl)

    def __hash__(self) -> int:
        return hash(self.address) if self.address != None else hash(self.symbol)

    def from_dict(dict_obj = {}, address=None):
        _address = dict_obj.get('address', None)

        return Token(dict_obj.get('symbol', None), dict_obj.get('name', None), dict_obj.get('market_cap', None), dict_obj.get('price_usd', None),
                     _address if _address is not None else address) \
            if dict_obj is not None else Token(address=address)

    def metadata(self) -> dict:
        """Populate token with all the data we can gather from many different sources"""
        _cached_metadata = self.get('metadata')
        _metadata = None if _cached_metadata is None else _cached_metadata

        if _metadata != None:
            return _metadata

        mixed_metadata = {}

        # fetch data collected by the TokensExtractor
        _metadata = get_token_by_address(self.address)

        # start fetching from other sources
        _alchemy_metadata = self.fetch_alchemy_metadata()
        _ethplorer_metadata = self.fetch_ethplorer_metadata()

        # combine all the data
        if _metadata is not None:
            mixed_metadata = {**mixed_metadata, **_metadata}

        if _alchemy_metadata is not None:
            mixed_metadata = {**mixed_metadata, **_alchemy_metadata}

        if _ethplorer_metadata is not None:
            mixed_metadata = {**mixed_metadata, **_ethplorer_metadata}

        _metadata = valfilter(lambda v: v != None, mixed_metadata)

        # cache the metadata
        if _metadata != None and len(_metadata) > 0:
            self.set('metadata', _metadata)

        return _metadata

    def fetch_ethplorer_metadata(self) -> dict:
        # we don't need anything extra than these attributes
        if self.price_usd != None and self.market_cap != None and self.address != None:
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
            print({'error': error.with_traceback(), 'token': str(self)})
        finally:
            return self._ethplorer_metadata

    def fetch_alchemy_metadata(self) -> dict:
        # only useful thing provided here is decimals
        if self.decimals != None:
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
            print({'error': error, 'token': str(self)})
        finally:
            return self._alchemy_metadata

    def __str__(self):
        return str({
            'symbol': self.symbol,
            'address': self.address,
            'market_cap': self.market_cap,
            'price_usd': self.price_usd,
            'decimals': self.decimals
        })
