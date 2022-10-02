from time import sleep
from com.cryptobot.classifiers.mempool_whales_tx import MempoolWhaleTXClassifier
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.ethereum import fetch_mempool


class MempoolExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

        self.whales_classifier = MempoolWhaleTXClassifier()

    def listen(self):
        self.logger.info('Monitoring the mempool...')

        while (True):
            mempool = fetch_mempool()
            mempool = self.whales_classifier.classify(mempool)

            sleep(1)

            self.logger.info(mempool, format=True)

    def run(self):
        self.listen()
