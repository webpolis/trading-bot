import datetime
import re
from com.cryptobot.config import Config
from com.cryptobot.strategies.strategy import StrategyAction, StrategyInput, StrategyResponse
from com.cryptobot.strategies.swap_strategy import (SwapStrategy,
                                                    SwapStrategyMetadata)
from com.cryptobot.utils.gbq import publish_to_table, query_table
from com.cryptobot.schemas.swap_tx import SwapTx
from pypika import Criterion, Order, Query, Table


class WhaleBuyStrategy(SwapStrategy):
    def __init__(self):
        super().__init__(__name__, ignore_stablecoins={
            'token_to': True, 'token_from': False})

        self.settings = Config().get_settings().runtime.strategies.whale_buy

    def apply(self, input: StrategyInput) -> StrategyResponse:
        response = super().apply(input)
        metadata: SwapStrategyMetadata = input.metadata
        tx: SwapTx = input.tx

        if metadata is None or len(metadata) == 0:
            self.logger.info('No metadata was generated.')

            return super().apply(input)

        time_window = datetime.datetime.utcnow(
        ) - datetime.timedelta(seconds=self.settings.lookup_token_buy_time)
        table_path = f'{Config().get_settings().gbq.project_id}.{Config().get_settings().gbq.dataset_id}.{self.settings.gbq_table}'
        table = Table(table_path)

        # retrieve latest whales' acquisitions for same token
        q = Query.from_(table).select('*').where(
            # is whale?
            Criterion.any([
                Criterion.all([
                    # does it holds more than #% of a token's market cap?
                    ((table.sender_token_to_qty_usd*100) / \
                     table.token_to_market_cap) >= self.settings.whale_token_market_percent,
                    # and does it holds a total portfolio value >= $#### ?
                    table.sender_total_usd >= self.settings.whale_wallet_value_threshold_usd
                ]), \
                # otherwise, does it holds a total portfolio value >= $#### ?
                table.sender_total_usd >= self.settings.whale_total_threshold_usd
            ]) \
            & Criterion.all([
                # buying token
                table.token_to_address == metadata['token_to_address'][0],
                # avoid div by zero
                table.token_to_market_cap > 0,
                # time window
                table.tx_timestamp >= time_window,
                Criterion.any([
                    # ignore failed transactions
                    table.tx_status == True,
                    # but keep in mind old dataset version (no status)
                    table.tx_status.isnull()
                ])
            ]),
        ).orderby('time_utc', order=Order.desc).limit(self.settings.lookup_token_buy_whales)
        sql = q.get_sql(quote_char=None)

        self.logger.info(f'Running query: {sql}')

        data = query_table(sql)

        if len(data) > 0:
            # check if whales have bought above certain threshold
            total_bought_usd = (data.token_to_qty*data.token_to_price_usd).sum() + \
                (metadata['token_to_qty'][0] * metadata['token_to_price_usd'][0])

            if total_bought_usd >= self.settings.whale_wallet_value_threshold_usd \
                    or total_bought_usd >= ((self.settings.whale_token_market_percent*metadata['token_to_market_cap'][0])/100):
                self.logger.info('We got a BUY signal.')

                metadata['buy'] = [True]

                response = StrategyResponse(
                    action=StrategyAction.BUY, token=tx.token_to, input=input)
            else:
                self.logger.info(
                    'This trade doesn\'t meet the criteria. No BUY signal.')

                metadata['buy'] = [False]
        else:
            self.logger.info(
                f'No previous whales action on this token since {time_window}.')

            metadata['buy'] = [False]

        publish_to_table(self.settings.gbq_table, metadata)

        return response
