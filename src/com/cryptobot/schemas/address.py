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
    def __init__(self, token: Token, balance: int):
        super().__init__()

        self.token = token
        self.balance = balance


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
