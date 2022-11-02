from com.cryptobot.config import Config
from com.cryptobot.strategies.swap_strategy import SwapStrategy, SwapStrategyMetadata
from com.cryptobot.strategies.strategy import StrategyInput, StrategyResponse
from com.cryptobot.utils.coingecko import is_stablecoin
from com.cryptobot.utils.gbq import publish_to_table
from pypika import Table, Query, Interval, Criterion


class WhaleBuyStrategy(SwapStrategy):
    def __init__(self):
        super().__init__(__name__)

        self.settings = Config().get_settings().runtime.strategies.whale_buy

    def apply(self, input: StrategyInput) -> StrategyResponse:
        """Sample query:
            SELECT
            *
            FROM
            `trading-bot-365802.trading_bot_data.WhaleBuySellStrategy`
            WHERE
            # is whale?
            ( (((sender_token_to_qty_usd*100)/token_to_market_cap) >= 1
                AND sender_total_usd >= 500000)
                OR sender_total_usd >= 1000000 )
            # avoid div by zero
            AND token_to_market_cap > 0
            ORDER BY
            time_utc DESC
            LIMIT
            1000
        Args:
            input (StrategyInput): _description_

        Returns:
            StrategyResponse: _description_
        """        
        metadata: SwapStrategyMetadata = input.metadata

        if len(metadata) == 0:
                self.logger.info('No metadata was generated.')

                return super().apply(input)

        if is_stablecoin(metadata['token_to']):
            self.logger.info(f"Ignoring stablecoin {metadata['token_to']}.")

            return super().apply(input)

        # publish_to_table(self.settings.gbq_table, metadata)

        return super().apply(input)
