from com.cryptobot.config import Config
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.token import Token
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.strategies.strategy import (Strategy, StrategyAction,
                                               StrategyResponse)
from com.cryptobot.utils.gbq import publish_to_table


class PortfolioAllocationStrategy(Strategy):
    def __init__(self):
        super().__init__(__name__)

        self.settings = Config().get_settings().runtime.strategies.portfolio_allocation

    def apply(self, tx: Tx | SwapTx) -> StrategyResponse:
        verdict = super().apply(tx)

        self.logger.info(f'Applying strategy for tx: {str(tx)}')

        # collect metadata from sender
        if hasattr(tx, 'token_from') and tx.token_from is not None:
            try:
                sender_stats = tx.sender.portfolio_stats()
                sender_token_stat = next(map(
                    lambda stat: stat if stat.balance.token.symbol == tx.token_from.symbol else None, sender_stats)) \
                    if sender_stats is not None else None

                print(sender_token_stat)
            except Exception as error:
                self.logger.error(error)
        else:
            self.logger.info('Not enough data for analysis.')

        # if (not hasattr(tx, 'token_from') or tx.token_from is None or sender_stats is None or len(sender_stats) == 0):
        #     # we don't have enough stats to proceed
        #     self.logger.info(
        #         f'Ignoring transaction since we have not collected enough data for strategy analysis: {str(tx)}')
        # else:
        #     self.logger.info(
        #         f'We have some token stats for this wallet\'s portfolio: {str(sender_stats)}')

        #     # @TODO: refactor calc
        #     verdict = StrategyResponse(action=StrategyAction.SELL, token=tx.token_from)

        # publish_to_table(self.__class__.__name__, {
        #     'tx_timestamp': [tx.timestamp],
        #     'hash': [tx.hash],
        #     'sender': [tx.sender.address],
        #     'receiver': [tx.receiver.address],
        #     'token_from': [tx.token_from.symbol if hasattr(tx, 'token_from') and tx.token_from is not None else None],
        #     'token_from_address': [tx.token_from.address if hasattr(tx, 'token_from') and tx.token_from is not None else None],
        #     'token_from_qty': [tx.token_from_qty if hasattr(tx, 'token_from_qty') else None],
        #     'token_to': [tx.token_to.symbol if hasattr(tx, 'token_to') and tx.token_to is not None else None],
        #     'token_to_address': [tx.token_to.address if hasattr(tx, 'token_to') and tx.token_to is not None else None],
        #     'token_to_qty': [tx.token_to_qty if hasattr(tx, 'token_to_qty') else None],
        # }, [{'name': 'token_from_qty', 'type': 'BIGNUMERIC'}, {'name': 'token_to_qty', 'type': 'BIGNUMERIC'}])

        return verdict
