from com.cryptobot.config import Config
from com.cryptobot.schemas.address import AddressPortfolioStats
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.token import Token
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.strategies.strategy import (Strategy, StrategyAction,
                                               StrategyResponse)
from com.cryptobot.utils.formatters import parse_token_qty
from com.cryptobot.utils.gbq import publish_to_table
from com.cryptobot.utils.trader import is_kucoin_listed


class PortfolioAllocationStrategy(Strategy):
    def __init__(self):
        super().__init__(__name__)

        self.settings = Config().get_settings().runtime.strategies.portfolio_allocation

    def apply(self, tx: Tx | SwapTx) -> StrategyResponse:
        verdict = super().apply(tx)

        self.logger.info(f'Applying strategy for tx {tx.hash}')

        # collect metadata from sender
        sender_stats = None
        sender_token_from_stats = None

        if hasattr(tx, 'token_from') and tx.token_from is not None:
            try:
                sender_stats = tx.sender.portfolio_stats()
                sender_token_from_stats: AddressPortfolioStats = next(iter([stat for stat in sender_stats if stat.balance.token == tx.token_from]), None) \
                    if sender_stats is not None and len(sender_stats) > 0 else None
            except Exception as error:
                self.logger.error(error)
        else:
            self.logger.info('Not enough data for analysis.')

        # collect values and prepare output
        has_token_from_stats = sender_token_from_stats != None
        token_from: Token = tx.token_from if hasattr(tx, 'token_from') else None
        token_from_qty = parse_token_qty(token_from, tx.token_from_qty) if hasattr(
            tx, 'token_from_qty') else -1
        token_from_market_cap = token_from.market_cap if token_from != None \
            and token_from.market_cap != None else float(-1)
        token_to: Token = tx.token_to if hasattr(tx, 'token_to') else None
        token_to_qty = parse_token_qty(token_to, tx.token_to_qty) if hasattr(
            tx, 'token_to_qty') else -1
        token_to_market_cap = token_to.market_cap if token_to != None \
            and token_to.market_cap != None else float(-1)
        sender_token_from_qty = parse_token_qty(
            token_from, sender_token_from_stats.balance.qty) if has_token_from_stats else float(-1)
        sender_token_from_qty_usd = sender_token_from_stats.balance.qty_usd if has_token_from_stats else float(
            -1)
        sender_token_from_allocation = sender_token_from_stats.allocation_percent if has_token_from_stats else float(
            -1)
        sender_total_usd = sender_stats[0].total_usd if sender_stats != None and len(sender_stats) > 0 else float(
            -1)
        kucoin_listed = is_kucoin_listed(token_from)
        ftx_listed = is_kucoin_listed(token_from)

        output = {
            'tx_timestamp': [tx.timestamp],
            'hash': [tx.hash],
            'sender': [str(tx.sender)],
            'sender_token_from_qty': [sender_token_from_qty],
            'sender_token_from_qty_usd': [sender_token_from_qty_usd],
            'sender_token_from_allocation': [sender_token_from_allocation],
            'sender_total_usd': [sender_total_usd],
            'receiver': [str(tx.receiver)],
            'token_from': [token_from.symbol if token_from != None else None],
            'token_from_address': [token_from.address if token_from != None else None],
            'token_from_qty': [token_from_qty],
            'token_from_market_cap': [token_from_market_cap],
            'token_to': [token_to.symbol if token_to != None else None],
            'token_to_address': [token_to.address if token_to != None else None],
            'token_to_qty': [token_to_qty],
            'token_to_market_cap': [token_to_market_cap],
            'is_kucoin_listed': [kucoin_listed],
            'is_ftx_listed': [ftx_listed]
        }

        publish_to_table(self.__class__.__name__, output)

        self.logger.info(str(output))

        return verdict
