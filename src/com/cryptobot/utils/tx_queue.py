import itertools
from heapq import heappop, heappush
import logging
from threading import Lock

from com.cryptobot.utils.logger import PrettyLogger


class TXQueue():
    lock = Lock()
    pq = []                         # list of entries arranged in a heap
    entry_finder = {}               # mapping of txs to entries
    REMOVED = '<removed-tx>'      # placeholder for a removed tx
    counter = itertools.count()     # unique sequence count

    def __init__(self):
        self.logger = PrettyLogger(__name__, logging.INFO)

    def count(self):
        count = self.counter

        return count

    def has_tx(self, tx: str):
        with self.lock:
            try:
                tx = hash(tx)
                has_hash = tx in self.entry_finder
            except Exception as error:
                self.logger.error(error)

                raise error

            return has_hash

    def add_tx(self, tx: str, priority=0):
        with self.lock:
            try:
                tx = hash(tx)

                'Add a new tx or update the priority of an existing tx'
                if tx in self.entry_finder:
                    self.remove_tx(tx)

                count = next(self.counter)
                entry = [priority, count, tx]
                self.entry_finder[tx] = entry

                heappush(self.pq, entry)
            except Exception as error:
                self.logger.error(error)

                return None

    def remove_tx(self, tx: str):
        'Mark an existing tx as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(tx)
        entry[-1] = self.REMOVED

    def pop_tx(self):
        'Remove and return the lowest priority tx. Raise KeyError if empty.'
        while self.pq:
            priority, count, tx = heappop(self.pq)

            if tx is not self.REMOVED:
                del self.entry_finder[tx]

                return tx

        raise KeyError('pop from an empty priority queue')
