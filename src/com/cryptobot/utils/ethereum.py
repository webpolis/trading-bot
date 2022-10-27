import json
from web3 import Web3

from com.cryptobot.config import Config
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.request import HttpRequest

settings = Config().get_settings()
w3Http = Web3(Web3.HTTPProvider(settings.web3.providers.infura.http))
cached_abis = {}


def is_contract(address: str):
    address = Web3.toChecksumAddress(address.lower())
    code = w3Http.eth.get_code(address)

    return code != b''


def fetch_mempool_txs():
    pending_block = w3Http.eth.getBlock(
        block_identifier='pending', full_transactions=True)
    pending_transactions = pending_block['transactions']

    return pending_transactions


def fetch_fake_mempool_txs():
    txs_hashes = json.load(open(get_data_path() + 'fake_mempool_transactions.json'))
    txs = []

    for tx_hash in txs_hashes:
        txs.append(w3Http.eth.get_transaction(tx_hash))

    return txs


def client():
    return w3Http


def get_contract_abi(address):
    address = address.lower()

    if address in cached_abis and cached_abis[address] != None:
        return cached_abis[address]

    abi_endpoint = settings.endpoints.etherscan.abis.format(
        address, settings.endpoints.etherscan.api_key)
    response = HttpRequest().get(abi_endpoint)
    cached_abis[address] = None

    if response['message'] == 'NOTOK':
        return None

    try:
        cached_abis[address] = json.loads(response['result'])
    except Exception as error:
        print({'error': error, 'response': response})

    return cached_abis[address]


def get_contract(address):
    abi = get_contract_abi(address)

    if abi == None:
        return None

    return w3Http.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)
