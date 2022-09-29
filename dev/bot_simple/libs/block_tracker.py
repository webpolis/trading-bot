import json
import time

import requests


class BlockTracker:
    def __init__(self):
        self.etherscan_api_key = "ISK12FCRKH4Z2JDHQBA2ZGUMAW5J844RZE"

    def get_last_block(self, address):
        return int(json.loads(requests.get(
            f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={round(time.time())}"
            f"&closest=before&apikey={self.etherscan_api_key}"
        ).text)["result"])


    def get_last_block(self, address):
        return int(json.loads(requests.get(
            f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={round(time.time())}"
            f"&closest=before&apikey={self.etherscan_api_key}"
        ).text)["result"])

    def get_last_txs(self, address, since=2):
        return json.loads(requests.get(
            f"https://api.etherscan.io/api?module=account&action=txlist&address={address}"
            f"&startblock={self.get_last_block(address) - since}&sort=asc&apikey={self.etherscan_api_key}"
        ).text)["result"]


if __name__ == '__main__':
    tracker = BlockTracker
