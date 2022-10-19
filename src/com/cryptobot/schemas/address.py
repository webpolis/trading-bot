import functools
import operator
from typing import List

from com.cryptobot.config import Config
from com.cryptobot.schemas.schema import Schema
from com.cryptobot.schemas.token import Token
from com.cryptobot.utils.ethereum import is_contract
from com.cryptobot.utils.pandas import get_address_details
from com.cryptobot.utils.request import HttpRequest

request = HttpRequest()
settings = Config().get_settings()


class AddressBalance(Schema):
    def __init__(self, token: Token, qty: int):
        super().__init__()

        self.token = token
        self.qty = qty
        self.qty_usd = (qty/10**token.decimals) * \
            token.price_usd if token.price_usd is not None else 0


class AddressPortfolioStats(Schema):
    def __init__(self, balance: AddressBalance, total_usd: float) -> None:
        super().__init__()

        self.balance = balance
        self.total_usd = total_usd
        self.allocation_percent = (
            self.balance.qty_usd*100)/self.total_usd \
            if self.balance.qty_usd != 0 and self.total_usd != 0 else 0


class Address(Schema):
    def __init__(self, address):
        super().__init__()

        self.address = address
        self.balances: List[AddressBalance] = []

    def metadata(self) -> dict:
        return get_address_details(self.address)

    def is_contract(self):
        return is_contract(self.address)

    def __str__(self):
        return self.address

    def get_balances(self) -> List[AddressBalance]:
        """Fetch once per iteration as it's cached in self.balances
        """

        self.balances = []
        payload = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'alchemy_getTokenBalances',
            'params': [self.address]
        }

        try:
            response = request.post(settings.endpoints.alchemy.api.format(
                api_key=settings.web3.providers.alchemy.api_key), payload)
            balances = response['result']['tokenBalances']

            for balance in balances:
                token = Token(address=balance['contractAddress'])
                qty = int(balance['tokenBalance'], 0)
                address_balance = AddressBalance(token, qty)

                self.balances.append(address_balance)
        except Exception as error:
            pass
        finally:
            return self.balances

    def portfolio_stats(self) -> List[AddressPortfolioStats]:
        stats: List[AddressPortfolioStats] = []
        balances = self.get_balances()
        total_usd = functools.reduce(
            operator.add, [
                balance.qty_usd
                for balance in balances if balance.qty_usd is not None],
            0
        )

        for balance in balances:
            stats.append(AddressPortfolioStats(balance, total_usd))

        return [stat for stat in stats if stat.balance.qty_usd is not None]
