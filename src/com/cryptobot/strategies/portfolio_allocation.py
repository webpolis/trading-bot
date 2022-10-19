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

        self.logger.info(f'Applying strategy for tx {tx.hash}')

        # collect metadata from sender
        if hasattr(tx, 'token_from') and tx.token_from is not None:
            try:
                sender_stats = tx.sender.portfolio_stats()
                sender_token_stats = next(map(
                    lambda stat: stat if stat.balance.token.symbol == tx.token_from.symbol else None, sender_stats), None) \
                    if sender_stats is not None and len(sender_stats) > 0 else None

                self.logger.info({'sender_stats': sender_stats,
                                 'sender_token_stats': sender_token_stats})
            except Exception as error:
                self.logger.error(error)
        else:
            self.logger.info('Not enough data for analysis.')

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
