from time import sleep
from com.cryptobot.extractors.extractor import Extractor
from com.cryptobot.utils.ethereum import fetch_mempool


class MempoolExtractor(Extractor):
    def __init__(self):
        super().__init__(__name__)

    def listen(self):
        self.logger.info('Watching the mempool...')

        while (True):
            mempool = fetch_mempool()

            sleep(1)

            self.logger.info(mempool)

    def run(self):
        self.listen()
