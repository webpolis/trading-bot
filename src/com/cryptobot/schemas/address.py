import math
import traceback
from typing import List

from jsonpickle import encode, decode
from com.cryptobot.config import Config
from com.cryptobot.schemas.schema import Schema
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.alchemy import api_post
from com.cryptobot.utils.network import is_contract
from com.cryptobot.utils.ethplorer import get_address_info
from com.cryptobot.utils.pandas_utils import get_address_details
from com.cryptobot.utils.redis_mixin import RedisMixin

settings = Config().get_settings()


class AddressBalance(Schema):
    def __init__(self, address: str, token: Token, qty: int = 0):
        super().__init__()

        self.address = address
        self.token = token
        self.qty = qty
        self.qty_usd = float(0)

        if (type(self.qty) == int or type(self.qty) == float) \
                and type(self.token.decimals) == int \
                and type(self.token.price_usd) == float \
                and self.token.decimals < 100:  # prevent Overflow error (ehtplorer gives odd stuff w/0x0911ee3fa4c45fd68601cb4206c09b4afc84c384)
            try:
                self.qty_usd = float(
                    (self.qty/10**self.token.decimals) * self.token.price_usd)
            except Exception as error:
                print(error)
                print(traceback.format_exc())

    def __str__(self):
        return str(self.__dict__)

    @property
    def __key__(self):
        return (self.token.__key__, self.qty)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) \
            and (self.address == other.address) \
            and (self.token.address == other.token.address)

    def __hash__(self) -> int:
        return hash((self.address, self.token.address))

    @property
    def __dict__(self):
        return {
            'token': self.token.__dict__,
            'qty': self.qty,
            'qty_usd': self.qty_usd
        }


def merge_address_balances(balances1: AddressBalance, balances2: AddressBalance):
    shared_balances = list(set(balances1) & set(balances2))
    balancesA = list(set(balances1) - set(balances2))
    balancesB = list(set(balances2) - set(balances1))

    return shared_balances + balancesA + balancesB


class AddressPortfolioStats(Schema):
    def __init__(self, balance: AddressBalance, total_usd: float = 0) -> None:
        super().__init__()

        self.balance = balance
        self.total_usd = total_usd
        self.allocation_percent = (
            self.balance.qty_usd*100)/self.total_usd \
            if self.balance.qty_usd != 0 and self.total_usd != 0 else float(0)

    def __str__(self):
        return str(self.__dict__)


class Address(Schema, RedisMixin):
    def __init__(self, address):
        for base_class in Address.__bases__:
            base_class.__init__(self)

        self.address = address.lower()

    @property
    def __key__(self):
        return (self.address)

    def metadata(self) -> dict:
        return get_address_details(self.address)

    def is_contract(self):
        return is_contract(self.address)

    def __str__(self):
        return self.address

    def balances_alchemy(self) -> List[AddressBalance]:
        balances = []

        try:
            page_key = None

            while True:
                params = [self.address, 'erc20']

                if page_key is not None:
                    params.append({'pageKey': page_key})

                payload = {
                    'id': 1,
                    'jsonrpc': '2.0',
                    'method': 'alchemy_getTokenBalances',
                    'params': params
                }

                print(f'Fetching balances for {self.address} (pageKey: {page_key})')

                try:
                    response = api_post(payload)
                except Exception as _error:
                    print(_error)
                    print(traceback.format_exc())

                    continue

                page_key = response.get('result', {}).get('pageKey', None)
                tokens_balances = response.get('result', {}).get('tokenBalances', None)

                if tokens_balances is not None:
                    for balance in tokens_balances:
                        token_balance = balance.get('tokenBalance', '0')
                        qty = int(token_balance, 0) if token_balance != '0x' else 0

                        if qty == 0:
                            continue

                        token = Token(address=balance['contractAddress'])
                        address_balance = AddressBalance(self.address, token, qty)

                        balances.append(address_balance)
                else:
                    print(f'No balances for {self.address}.')

                if page_key is None:
                    break
        except Exception as error:
            print(error)
            print(traceback.format_exc())
        finally:
            return balances

    def balances_ethplorer(self) -> List[AddressBalance]:
        balances = []

        try:
            response = get_address_info(self.address)

            if type(response) == type([]):
                for balance in response:
                    token_info = balance.get('tokenInfo', None)
                    qty = balance.get('balance', None)

                    if token_info != None:
                        try:
                            address = token_info.get('address', None)
                            name = token_info.get('name', None)
                            symbol = token_info.get('symbol', None)
                            decimals = token_info.get('decimals', None)
                            price = token_info.get('price', {})
                            price_usd = float(price.get('rate')) if type(
                                price) == dict else None
                            market_cap = float(price.get('marketCapUsd')) if type(
                                price) == dict else None

                            token = Token(symbol, name, market_cap,
                                          price_usd, address, int(decimals) if decimals != None else None)

                            address_balance = AddressBalance(self.address, token, qty)

                            balances.append(address_balance)
                        except Exception as _error:
                            print({'error': _error, 'balance': str(balance)})
                            print(traceback.format_exc())
        except Exception as error:
            print(error)
            print(traceback.format_exc())
        finally:
            return balances

    def balances_explorer(self) -> List[AddressBalance]:
        return []

    def portfolio_stats(self) -> List[AddressPortfolioStats]:
        cached_portfolio_stats = self.get('portfolio_stats')
        cached_portfolio_stats = [decode(
            stat) for stat in cached_portfolio_stats] if cached_portfolio_stats != None else []
        stats: List[AddressPortfolioStats] = [
        ] if cached_portfolio_stats is None else cached_portfolio_stats

        if len(stats) > 0:
            return stats

        try:
            balances_ethplorer = self.balances_ethplorer()
            balances_explorer = self.balances_explorer()
            tokens_ethplorer = sorted(
                list(set([b.token.symbol for b in balances_ethplorer])))
            tokens_explorer = sorted(
                list(set([b.token.symbol for b in balances_explorer])))
            address_tokens = sorted(list(set(tokens_ethplorer+tokens_explorer)))
            address_balances = merge_address_balances(
                balances_ethplorer, balances_explorer)

            print(
                f'Retrieved {len(balances_ethplorer)} balance(s) for {self.address} via ethplorer')
            print(
                f'Retrieved {len(balances_explorer)} balance(s) for {self.address} via explorer')
            print(
                f'Address {self.address} owns: {address_tokens}')

            total_usd = 0

            for balance in address_balances:
                if type(balance.qty_usd) == float and not math.isnan(balance.qty_usd):

                    total_usd += balance.qty_usd

            for balance in address_balances:
                stats.append(AddressPortfolioStats(balance, total_usd))
        except Exception as error:
            print(error)
            print(traceback.format_exc())
        finally:
            if len(stats) > 0:
                self.set('portfolio_stats', [encode(stat,  max_depth=3) for stat in stats],
                         ttl=settings.runtime.schemas.address.portfolio_stats_cache_timeout)

            return stats
