import logging
from typing import List

from com.cryptobot.events.producer import EventsProducerMixin
from com.cryptobot.utils.logger import PrettyLogger
from rsmq.consumer import RedisSMQConsumerThread


class EventsConsumerMixin():
    def __init__(self, queues: List[str] | str, *args, **kwargs) -> None:
        self._logger = PrettyLogger(__name__, logging.INFO)
        self.host = '127.0.0.1'
        self.port = 6379
        self.trace = True
        self.vt = 30
        self.delay = 0
        self.ns = EventsProducerMixin.__name__
        self.queues = [queues] if type(queues) != type([]) else queues
        self.consumers = {}

        for queue in self.queues:
            self.consumers[queue] = RedisSMQConsumerThread(
                qname=queue, processor=self.process, host=self.host, port=self.port,
                ns=self.ns, vt=self.vt, empty_queue_delay=2, trace=self.trace, decode=True)

    def consume(self):
        for queue in self.queues:
            self.logger.info(f'Listening to {queue} queue')

            self.consumers[queue].start()
