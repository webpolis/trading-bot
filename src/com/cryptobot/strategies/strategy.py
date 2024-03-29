import logging
import json
from typing import TypedDict

from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.schemas.token import Token
from enum import Enum


class StrategyAction(Enum):
    NONE = 0
    BUY = 1
    SELL = 2


class StrategyMetadata(TypedDict):
    tx: str
    sender: str
    receiver: str


class StrategyInput:
    tx: Tx
    metadata: StrategyMetadata

    def __init__(self, tx: Tx, metadata: StrategyMetadata = None) -> None:
        self.tx = tx
        self.metadata = metadata


class StrategyResponse:
    action: StrategyAction
    token: Token | None
    input: StrategyInput | None

    def __init__(self, action: StrategyAction = StrategyAction.NONE, token: Token = None, input: StrategyInput = None):
        """The response from an applied strategy.

        Args:
            action (StrategyAction, optional): The action can be either NONE,BUY,SELL. Defaults to StrategyAction.NONE.
            token (Token, optional): The token for which the action has to be done. Defaults to None.
            input (StrategyInput, optional): The original strategy's input. Defaults to None.
        """
        self.action = action
        self.token = token
        self.input = input

    def __str__(self):
        return str({
            'action': self.action,
            'token': self.token.symbol if self.token != None else None,
            'metadata': self.input.metadata if self.input != None else None,
            'tx': self.input.tx.hash
        })


class Strategy:
    def __init__(self, cls):
        self.cls = cls
        self.logger = PrettyLogger(cls, logging.INFO)

        self.logger.info('Initialized.')

    def metadata(self, tx: Tx) -> StrategyMetadata:
        """Generates the metadata required to make a decision.
        Any custom calculation and logic can be arranged here.

        Args:
            tx (Tx): The current transaction

        Returns:
            StrategyMetadata: A dictionary based output
        """
        return dict()

    def apply(self, input: StrategyInput) -> StrategyResponse:
        """Applies the strategy logic.

        Args:
            input (StrategyInput): An input containing the transaction and any metadata
            generated.

        Returns:
            StrategyResponse: The action to be taken.
        """
        return StrategyResponse(input=input)

    @property
    def __key__(self):
        return (None)

    def __hash__(self):
        return hash(self.__key__)
