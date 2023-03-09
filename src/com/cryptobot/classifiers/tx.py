from typing import List

from com.cryptobot.classifiers.classifier import Classifier
from com.cryptobot.schemas.tx import Tx
from com.cryptobot.utils.formatters import tx_parse
from com.cryptobot.utils.tx_queue import TXQueue
from com.cryptobot.config import Config


class TXClassifier(Classifier):
    def __init__(self, cls=__name__, cache: TXQueue = None):
        super().__init__(cls)

        self.cache = cache

        settings = Config().get_settings().runtime.classifiers
        self.settings = settings.TXClassifier if hasattr(
            settings, 'TXClassifier') else None

    def parse(self, items) -> List[Tx]:
        if (len(items) > 0 and type(items[0]) == Tx):
            return items

        items = super().parse(items)
        tx_root_key = self.settings.tx_root_key if self.settings != None else None
        txs: List[Tx] = list(map(lambda item: tx_parse(
            item[tx_root_key] if tx_root_key != None and tx_root_key in item else item), items))

        return txs
