from enum import Enum
import json
import re
from web3 import Web3
from polygonscan import PolygonScan
from com.cryptobot.config import Config
from com.cryptobot.utils.path import get_data_path
from com.cryptobot.utils.request import HttpRequest

settings = Config().get_settings()
request = HttpRequest()
w3Http = Web3(Web3.HTTPProvider(settings.web3.providers.infura.http))
cached_abis = {}


class ProviderNetwork(Enum):
    ETHEREUM = 0
    POLYGON = 1
    ARBITRUM = 2


def is_contract(address: str):
    address = Web3.toChecksumAddress(address.lower())
    code = w3Http.eth.get_code(address)

    return code != b''


def is_eth_address(address: str):
    return int(address.lower(), 0) == 0 or address.lower() == '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'


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
    network = get_current_network()

    if network == ProviderNetwork.ETHEREUM:
        abi = get_contract_abi(address)
    elif network == ProviderNetwork.POLYGON:
        with PolygonScan(settings.endpoints.polygonscan.api_key, False) as polygon:
            abi = polygon.get_contract_abi(address)
    elif network == ProviderNetwork.ARBITRUM:
        url = settings.endpoints.arbitrumscan.contract_abi.format(address=address)
        response = request.get(url)
        abi = json.loads(response['result']) if response['status'] != '0' else None

    if abi == None:
        return None

    return w3Http.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)


def get_tx_receipt(hash: str):
    return w3Http.eth.get_transaction_receipt(hash)


def get_current_network():
    if re.match(r'^.*polygon.*$', settings.web3.providers.infura.http, flags=re.IGNORECASE):
        return ProviderNetwork.POLYGON

    if re.match(r'^.*arbitrum.*$', settings.web3.providers.infura.http, flags=re.IGNORECASE):
        return ProviderNetwork.ARBITRUM

    return ProviderNetwork.ETHEREUM


def get_network_suffix():
    network = get_current_network()
    suffix = f'_{str(network).split(".")[-1]}_' if network != ProviderNetwork.ETHEREUM else ''

    return suffix


def get_network_name():
    lsuffix = get_network_suffix().lower()

    return re.sub(r'[^a-z]*', '', lsuffix, flags=re.IGNORECASE)
