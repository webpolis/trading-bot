from com.cryptobot.schemas.schema import Schema
from com.cryptobot.utils.ethereum import is_contract
from com.cryptobot.utils.pandas import get_address_details


class Address(Schema):
    def __init__(self, address):
        super().__init__()

        self.address = address

    def metadata(self) -> dict:
        return get_address_details(self.address)

    def is_contract(self):
        return is_contract(self.address)

    def __str__(self):
        return self.address
