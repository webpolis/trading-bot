from com.cryptobot.strategies.strategy import Strategy, StrategyResponse, StrategyAction
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.schemas.token import Token
from com.cryptobot.config import Config
from com.cryptobot.schemas.swap_tx import SwapTx


class PortfolioAllocationStrategy(Strategy):
    def __init__(self):
        super().__init__(__name__)

        self.settings = Config().get_settings().runtime.strategies.portfolio_allocation

    def apply(self, tx: Tx | SwapTx) -> StrategyResponse:
        metadata: dict = tx.metadata()
        token_from_stats = metadata.get('token_from')
        token_to_stats = metadata.get('token_to')
        sender_stats = metadata['sender'] if len(metadata['sender']) > 0 else None
        receiver_stats = metadata['receiver'] if len(metadata['receiver']) > 0 else None

        # we don't have enough stats to proceed
        if token_from_stats is None or sender_stats is None:
            self.logger.info(
                f'This is not an interesting transaction since we have not collected any data for it: {str(tx)}')

            return super().apply(tx)

        wallet_token_stats = sender_stats[sender_stats['token_symbol']
                                          == token_from_stats['symbol']]

        if len(wallet_token_stats) > 0:
            if wallet_token_stats['wallet_portfolio_alloc'] >= self.settings.min_wallet_portfolio_alloc:
                if wallet_token_stats['wallet_market_percent'] >= self.settings.min_wallet_market_percent:
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

        return super().apply(tx)
