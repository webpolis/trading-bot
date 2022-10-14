from time import sleep
from typing import List

from com.cryptobot.classifiers.mempool_whales_tx import \
    MempoolWhaleTXClassifier
from com.cryptobot.classifiers.swap_classifier import SwapClassifier
from com.cryptobot.classifiers.tx_classifier import TXClassifier
from com.cryptobot.config import Config
from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.ethereum import fetch_mempool_txs
from com.cryptobot.utils.tx_queue import TXQueue


class MempoolExtractor(Extractor, EventsProducerMixin):
    def __init__(self):
        for base_class in MempoolExtractor.__bases__:
            base_class.__init__(self, __name__)

        self.cached_txs = TXQueue()
        self.whales_classifier = MempoolWhaleTXClassifier()

    def listen(self):
        self.logger.info('Monitoring the mempool...')
        max_concurrent_threads = Config().get_settings(
        ).runtime.classifiers.swap.max_concurrent_threads

        for i in range(0, max_concurrent_threads):
            SwapClassifier(self.cached_txs).consume()

        while (True):
            try:
                mempool_txs_orig = fetch_mempool_txs()
                mempool_txs = self.whales_classifier.classify(mempool_txs_orig)
                # mempool_txs = TXClassifier().classify(mempool_txs_orig)  # for devs only

                if len(mempool_txs) > 0:
                    current_block = mempool_txs[0].block_number

                    self.logger.info(
                        f'{len(mempool_txs)} transactions coming from whales have caught our attention at block #{current_block} and we\'ll start classifying them.')

                    self.publish(list(map(lambda tx: str(tx), mempool_txs)))
            except Exception as error:
                self.logger.error(error)
            finally:
                sleep(1)

    def run(self):
        self.listen()
