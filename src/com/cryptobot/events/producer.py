import logging
import time
from rsmq import RedisSMQ

from com.cryptobot.utils.logger import PrettyLogger


class EventsProducerMixin():
    def __init__(self, *args, **kwargs) -> None:
        self._logger = PrettyLogger(__name__, logging.INFO)
        self.queue = args[0]
        self.host = '127.0.0.1'
        self.port = 6379
        self.trace = True
        self.vt = 30
        self.delay = 0
        self.ns = EventsProducerMixin.__name__

        self.rsmq_producer = RedisSMQ(qname=self.queue, host=self.host,
                                      port=self.port, ns=self.ns, vt=self.vt,
                                      delay=self.delay, trace=self.trace)

        self.rsmq_producer.deleteQueue(qname=self.queue, quiet=True).exceptions(
            False).execute()
        self.rsmq_producer.createQueue(
            qname=self.queue, quiet=True).exceptions(False).execute()

        self._logger.info(f'Created queue {self.queue}')

    def publish(self, msg=None, debug=False):
        if msg is None:
            return

        msg_id = self.rsmq_producer.sendMessage(message={
            'item': msg,
            'ts': time.time()
        }, encode=True).execute()

        if debug:
            self.logger.info(f'Published new msg #{msg_id} in queue {self.queue}')

        return msg_id
