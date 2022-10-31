from com.cryptobot.config import Config
from com.cryptobot.strategies.swap_strategy import SwapStrategy, SwapStrategyMetadata
from com.cryptobot.strategies.strategy import StrategyInput, StrategyResponse
from com.cryptobot.utils.gbq import publish_to_table


class WhaleBuySellStrategy(SwapStrategy):
    def __init__(self):
        super().__init__(__name__)

        self.settings = Config().get_settings().runtime.strategies.whale_buy_sell

    def apply(self, input: StrategyInput) -> StrategyResponse:
        metadata: SwapStrategyMetadata = input.metadata

        publish_to_table(self.__class__.__name__, metadata)

        return super().apply(input)
