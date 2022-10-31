from com.cryptobot.config import Config
from com.cryptobot.strategies.swap_strategy import SwapStrategy, SwapStrategyMetadata
from com.cryptobot.strategies.strategy import StrategyInput, StrategyResponse
from com.cryptobot.utils.gbq import publish_to_table
from pypika import Table, Query, Interval, Criterion


class WhaleBuySellStrategy(SwapStrategy):
    def __init__(self):
        super().__init__(__name__)

        self.settings = Config().get_settings().runtime.strategies.whale_buy_sell

    def apply(self, input: StrategyInput) -> StrategyResponse:
        metadata: SwapStrategyMetadata = input.metadata

        if len(metadata) == 0:
            self.logger.info('No metadata for analysis.')

            return super().apply(input)

        publish_to_table(self.__class__.__name__, metadata)

        return super().apply(input)
