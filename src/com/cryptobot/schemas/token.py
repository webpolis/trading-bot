from com.cryptobot.schemas.schema import Schema


class Token(Schema):
    def __init__(self, symbol, name, address):
        self.symbol = symbol
        self.name = name
        self.address = address
