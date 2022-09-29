import whale


class Token:
    def __init__(self,
                 name,
                 symbol,
                 network):
        self.name = name
        self.symbol = symbol
        self.network = network
        self.price = None
        self.returns = None
        self.volatility = None
        self.whales = {}
        # for i in whale_number:
        #     self.whales[str(i)] = whale.Whale()


        
