from typing import List
from com.cryptobot.config import Config
from com.cryptobot.schemas.schema import Schema
from com.cryptobot.utils.ethereum import is_contract
from com.cryptobot.utils.pandas import get_address_details
from com.cryptobot.utils.request import HttpRequest

request = HttpRequest()
settings = Config().get_settings()


class AddressBalance(Schema):
    def __init__(self):
        super().__init__()


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

    def get_balances(self):
        payload = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'alchemy_getTokenBalances',
            'params': [self.address]
        }

        try:
            response = request.post(settings.endpoints.alchemy.token_balances.format(
                api_key=settings.web3.providers.alchemy.api_key), payload)

            return response['result']['tokenBalances']
        except Exception as error:
            return None
