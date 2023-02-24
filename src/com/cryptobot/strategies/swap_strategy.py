from datetime import datetime
from typing import TypedDict
from com.cryptobot.schemas.address import AddressPortfolioStats
from com.cryptobot.schemas.swap_tx import SwapTx
from com.cryptobot.schemas.token import Token
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.strategies.strategy import (Strategy, StrategyMetadata)
from com.cryptobot.utils.coingecko import is_stablecoin
from com.cryptobot.utils.formatters import parse_token_qty
from com.cryptobot.utils.redis_mixin import RedisMixin
from com.cryptobot.utils.trader import (get_btc_trend, is_ftx_listed,
                                        is_kucoin_listed)
from com.cryptobot.utils.network import get_tx_receipt


class SwapStrategyMetadata(StrategyMetadata):
    tx_timestamp: datetime
    tx_status: bool
    hash: str
    sender: str
    sender_token_from_qty: float
    sender_token_from_qty_usd: float
    sender_token_from_allocation: float
    sender_token_to_qty: float
    sender_token_to_qty_usd: float
    sender_token_to_allocation: float
    sender_total_usd: float
    receiver: str
    token_from: str
    token_from_address: str
    token_from_qty: float
    token_from_price_usd: float
    token_from_market_cap: float
    token_to: str
    token_to_address: str
    token_to_qty: float
    token_to_price_usd: float
    token_to_market_cap: float
    is_kucoin_listed: bool
    is_ftx_listed: bool
    btc_trend_7_days: float
    btc_trend_1_day: float
    buy: bool


class IgnoreStableOption(TypedDict):
    token_from: bool
    token_to: bool


class SwapStrategy(Strategy, RedisMixin):
    def __init__(self, cls=__name__, ignore_stablecoins: IgnoreStableOption = {'token_to': False, 'token_from': False}):
        super().__init__(cls)

        self.ignore_stablecoins = ignore_stablecoins

    @property
    def __key__(self):
        return (__name__)

    def metadata(self, tx: Tx | SwapTx) -> SwapStrategyMetadata:
        self.logger.info(f'Generating metadata for tx {tx.hash}')

        # collect metadata from sender
        sender_stats = None
        sender_token_from_stats = None
        sender_token_to_stats = None

        if hasattr(tx, 'token_from') and tx.token_from is not None:
            if self.ignore_stablecoins['token_from'] == True and is_stablecoin(tx.token_from.symbol):
                self.logger.info(
                    f"Ignoring token_from stablecoin {tx.token_from.symbol}.")

                return None

            if self.ignore_stablecoins['token_to'] == True and is_stablecoin(tx.token_to.symbol):
                self.logger.info(f"Ignoring token_to stablecoin {tx.token_to.symbol}.")

                return None

            try:
                sender_stats = tx.sender.portfolio_stats()
                sender_token_from_stats: AddressPortfolioStats = next(iter([stat for stat in sender_stats if stat.balance.token == tx.token_from]), None) \
                    if sender_stats is not None and len(sender_stats) > 0 else None
                sender_token_to_stats: AddressPortfolioStats = next(iter([stat for stat in sender_stats if stat.balance.token == tx.token_to]), None) \
                    if sender_stats is not None and len(sender_stats) > 0 else None
            except Exception as error:
                self.logger.error(error)
        else:
            self.logger.info(
                'Not enough data collected. Swap contract was probably not supported.')

            return super().metadata(tx)

        # collect values and prepare output
        has_token_from_stats = sender_token_from_stats != None
        has_token_to_stats = sender_token_to_stats != None
        token_from: Token = tx.token_from if hasattr(tx, 'token_from') else None
        token_from_qty = parse_token_qty(token_from, tx.token_from_qty) if hasattr(
            tx, 'token_from_qty') else float(-1)
        token_from_price_usd = token_from.price_usd if token_from != None and token_from.price_usd != None else float(
            -1)
        token_from_market_cap = token_from.market_cap if token_from != None \
            and token_from.market_cap != None else float(-1)
        token_to: Token = tx.token_to if hasattr(tx, 'token_to') else None
        token_to_qty = parse_token_qty(token_to, tx.token_to_qty) if hasattr(
            tx, 'token_to_qty') else float(-1)
        token_to_price_usd = token_to.price_usd if token_to != None and token_to.price_usd != None else float(
            -1)
        token_to_market_cap = token_to.market_cap if token_to != None \
            and token_to.market_cap != None else float(-1)
        sender_token_from_qty = parse_token_qty(
            token_from, sender_token_from_stats.balance.qty) if has_token_from_stats else float(-1)
        sender_token_from_qty_usd = sender_token_from_stats.balance.qty_usd if has_token_from_stats else float(
            -1)
        sender_token_from_allocation = sender_token_from_stats.allocation_percent if has_token_from_stats else float(
            -1)
        sender_token_to_qty = parse_token_qty(
            token_to, sender_token_to_stats.balance.qty) if has_token_to_stats else float(-1)
        sender_token_to_qty_usd = sender_token_to_stats.balance.qty_usd if has_token_to_stats else float(
            -1)
        sender_token_to_allocation = sender_token_to_stats.allocation_percent if has_token_to_stats else float(
            -1)
        sender_total_usd = sender_stats[0].total_usd if sender_stats != None and len(sender_stats) > 0 else float(
            -1)
        kucoin_listed = is_kucoin_listed(token_from) if token_from != None else False
        ftx_listed = is_ftx_listed(token_from) if token_from != None else False

        # bitcoin trend
        cached_btc_trend_7_days = self.get('btc_trend_7_days')
        btc_trend_7_days = cached_btc_trend_7_days if cached_btc_trend_7_days != None else get_btc_trend(
            days=7)
        cached_btc_trend_1_day = self.get('btc_trend_1_day')
        btc_trend_1_day = cached_btc_trend_1_day if cached_btc_trend_1_day != None else get_btc_trend(
            days=1)

        if btc_trend_7_days != cached_btc_trend_7_days:
            self.set('btc_trend_7_days', btc_trend_7_days, ttl=60*60*4)

        if btc_trend_1_day != cached_btc_trend_1_day:
            self.set('btc_trend_1_day', btc_trend_1_day, ttl=60*30)

        # check current status of transaction
        tx_status = True

        try:
            tx_receipt = get_tx_receipt(tx.hash)
            tx_status = tx_receipt.get('status', True) if tx_receipt != None else True
        except Exception as error:
            self.logger.error(error)

        metadata = {
            'tx_timestamp': [tx.timestamp],
            'hash': [tx.hash],
            'sender': [str(tx.sender)],
            'sender_token_from_qty': [sender_token_from_qty],
            'sender_token_from_qty_usd': [sender_token_from_qty_usd],
            'sender_token_from_allocation': [sender_token_from_allocation],
            'sender_token_to_qty': [sender_token_to_qty],
            'sender_token_to_qty_usd': [sender_token_to_qty_usd],
            'sender_token_to_allocation': [sender_token_to_allocation],
            'sender_total_usd': [sender_total_usd],
            'receiver': [str(tx.receiver)],
            'token_from': [token_from.symbol if token_from != None else None],
            'token_from_address': [token_from.address if token_from != None else None],
            'token_from_qty': [token_from_qty],
            'token_from_price_usd': [token_from_price_usd],
            'token_from_market_cap': [token_from_market_cap],
            'token_to': [token_to.symbol if token_to != None else None],
            'token_to_address': [token_to.address if token_to != None else None],
            'token_to_qty': [token_to_qty],
            'token_to_price_usd': [token_to_price_usd],
            'token_to_market_cap': [token_to_market_cap],
            'is_kucoin_listed': [kucoin_listed],
            'is_ftx_listed': [ftx_listed],
            'btc_trend_7_days': [btc_trend_7_days],
            'btc_trend_1_day': [btc_trend_1_day],
            'tx_status': [bool(tx_status)]
        }

        return SwapStrategyMetadata(metadata)
