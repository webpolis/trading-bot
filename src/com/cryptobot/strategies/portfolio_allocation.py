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
        # collect metadata from transaction
        metadata: dict = tx.metadata()
        token_from_stats = metadata.get('token_from')
        token_to_stats = metadata.get('token_to')
        sender_stats = metadata['sender'] if len(metadata['sender']) > 0 else None
        receiver_stats = metadata['receiver'] if len(metadata['receiver']) > 0 else None

        publish_to_table(self.__class__.__name__, {
            'tx_timestamp': [tx.timestamp],
            'hash': [tx.hash],
            'sender': [tx.sender],
            'receiver': [tx.receiver],
            'token_from': [tx.token_from if hasattr(tx, 'token_from') else None],
            'token_from_qty': [tx.token_from_qty if hasattr(tx, 'token_from_qty') else None],
            'token_to': [tx.token_to if hasattr(tx, 'token_to') else None],
            'token_to_qty': [tx.token_to_qty if hasattr(tx, 'token_to_qty') else None],
            # 'token_from_stats': [token_from_stats.to_json(index=False, orient='table') if token_from_stats != None else None],
            # 'token_to_stats': [token_to_stats.to_json(index=False, orient='table') if token_to_stats != None else None]
        }, [{'name': 'token_from_qty', 'type': 'BIGNUMERIC'}, {'name': 'token_to_qty', 'type': 'BIGNUMERIC'}])

        # we don't have enough stats to proceed
        if (token_from_stats is None or len(token_from_stats) == 0) or sender_stats is None:
            self.logger.info(
                f'Ignoring transaction since we have not collected enough data for strategy analysis: {str(tx)}')

            return super().apply(tx)

        wallet_token_stats = sender_stats[sender_stats['token_symbol']
                                          == str(token_from_stats.symbol.item())]

        if len(wallet_token_stats) > 0:
            self.logger.info(
                f'We have some token stats for this wallet\'s portfolio: {wallet_token_stats.to_json(orient="records")}')

            if wallet_token_stats['wallet_portfolio_alloc'].item() >= self.settings.min_wallet_portfolio_alloc:
                if wallet_token_stats['wallet_market_percent'].item() >= self.settings.min_wallet_market_percent:
                    # we are interested in trading this signal
                    return StrategyResponse(action=StrategyAction.SELL,
                                            token=Token(
                                                token_from_stats['symbol'],
                                                token_from_stats['name'],
                                                token_from_stats['market_cap'],
                                                token_from_stats['price_usd'],
                                                token_from_stats['address']
                                            )
                                            )
        else:
            self.logger.info(
                f'Not enough token stats for wallet: {wallet_token_stats.to_json(orient="records")}')

        return super().apply(tx)
