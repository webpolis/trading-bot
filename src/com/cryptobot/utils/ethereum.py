import json
from urllib import request
from web3 import Web3

from com.cryptobot.config import Config

settings = Config().get_settings()
w3Http = Web3(Web3.HTTPProvider(settings.web3.providers.infura.http))


def is_contract(address: str):
    address = Web3.toChecksumAddress(address.lower())
    code = w3Http.eth.get_code(address)

    return code != b''


def fetch_mempool_txs():
    pending_block = w3Http.eth.getBlock(
        block_identifier='pending', full_transactions=True)
    pending_transactions = pending_block['transactions']

    return pending_transactions


def client():
    return w3Http


def get_contract_abi(address):
    abi_endpoint = settings.endpoints.etherscan.abis.format(
        address, settings.endpoints.etherscan.api_key)

    abi = json.loads(request.get(abi_endpoint).text)

    return abi


def get_contract(address):
    abi = get_contract_abi(address)

    return w3Http.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
