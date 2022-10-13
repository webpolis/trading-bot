from heapq import heappop, heappush
import itertools

from com.cryptobot.schemas.tx import Tx


class TXQueue():
    pq = []                         # list of entries arranged in a heap
    entry_finder = {}               # mapping of txs to entries
    REMOVED = '<removed-tx>'      # placeholder for a removed tx
    counter = itertools.count()     # unique sequence count

    def count(self):
        return self.counter

    def add_tx(self, tx: Tx, priority=0):
        'Add a new tx or update the priority of an existing tx'
        if tx.hash in self.entry_finder:
            self.remove_tx(tx)

        count = next(self.counter)
        entry = [priority, count, tx]
        self.entry_finder[tx.hash] = entry

        heappush(self.pq, entry)

    def remove_tx(self, tx: Tx):
        'Mark an existing tx as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(tx.hash)
        entry[-1] = self.REMOVED

    def pop_tx(self):
        'Remove and return the lowest priority tx. Raise KeyError if empty.'
        while self.pq:
            priority, count, tx = heappop(self.pq)

            if tx is not self.REMOVED:
                del self.entry_finder[tx.hash]

                return tx

        raise KeyError('pop from an empty priority queue')
