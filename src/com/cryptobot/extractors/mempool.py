from time import sleep
from com.cryptobot.classifiers.mempool_whales_tx import MempoolWhaleTXClassifier
from com.cryptobot.classifiers.swap_classifier import SwapClassifier
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.ethereum import fetch_mempool_txs


class MempoolExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.whales_classifier = MempoolWhaleTXClassifier()
        self.swap_classifier = SwapClassifier()

    def listen(self):
        self.logger.info('Monitoring the mempool...')

        while (True):
            mempool_txs_orig = fetch_mempool_txs()
            mempool_txs = self.whales_classifier.classify(mempool_txs_orig)

            if len(mempool_txs) > 0:
                self.logger.info(
                    f'{len(mempool_txs)} transactions coming from whale(s) caught our attention at block #{mempool_txs[0].blockNumber} and we\'ll start classifying them.')

                # classify swap transactions
                swap_txs = self.swap_classifier.classify(mempool_txs)

                # feed event system

            sleep(1)

    def run(self):
        self.listen()
