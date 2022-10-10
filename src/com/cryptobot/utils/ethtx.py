from typing import List

from com.cryptobot.config import Config

from ethtx import EthTx, EthTxConfig
from ethtx.models.decoded_model import (DecodedBalance, DecodedCall,
                                        DecodedEvent, DecodedTransaction,
                                        DecodedTransfer)
from ethtx.models.objects_model import Block, Call, Event, Transaction
from ethtx.models.w3_model import W3Block, W3CallTree, W3Receipt, W3Transaction


class EthTxWrapper():
    def __init__(self) -> None:
        self.settings = Config().get_settings()
        self.ethtx_config = EthTxConfig(
            mongo_connection_string='mongomock://localhost/ethtx',
            etherscan_api_key=self.settings.endpoints.etherscan.api_key,
            web3nodes={
                self.settings.web3.chain_id: {
                    # multiple nodes supported, separate them with comma
                    'hook': self.settings.web3.providers.archivenode.http,
                    'poa': True
                }
            },
            default_chain=self.settings.web3.chain_id,
            etherscan_urls={
                self.settings.web3.chain_id: self.settings.endpoints.etherscan.api, },
        )

        self.ethtx = EthTx.initialize(self.ethtx_config)

    def get_raw_tx(self, tx: str):
        web3provider = self.ethtx.providers.web3provider

        # read raw transaction data directly from the node
        w3transaction: W3Transaction = web3provider.get_transaction(tx)
        w3receipt: W3Receipt = web3provider.get_receipt(w3transaction.hash.hex())
        w3calls: W3CallTree = web3provider.get_calls(w3transaction.hash.hex())

        return Transaction.from_raw(
            w3transaction=w3transaction, w3receipt=w3receipt, w3calltree=w3calls
        )

    def get_block(self, raw_tx: Transaction):
        return Block.from_raw(
            w3block=self.ethtx.providers.web3provider.get_block(
                raw_tx.metadata.block_number),
            chain_id=self.settings.web3.chain_id,
        )

    def get_decoded_components(self, raw_tx: Transaction):
        block = self.get_block(raw_tx)
        proxies = self.ethtx.decoders.get_proxies(
            raw_tx.root_call, self.settings.web3.chain_id)

        abi_decoded_calls: DecodedCall = self.ethtx.decoders.abi_decoder.decode_calls(
            raw_tx.root_call, block.metadata, raw_tx.metadata, proxies
        )
        abi_decoded_events: List[Event] = self.ethtx.decoders.abi_decoder.decode_events(
            raw_tx.events, block.metadata, raw_tx.metadata
        )
        abi_decoded_transfers: List[
            DecodedTransfer
        ] = self.ethtx.decoders.abi_decoder.decode_transfers(abi_decoded_calls, abi_decoded_events)
        # abi_decoded_balances: List[DecodedBalance] = self.ethtx.decoders.abi_decoder.decode_balances(
        #     abi_decoded_transfers
        # )

        return {
            'abi_decoded_calls': abi_decoded_calls,
            'abi_decoded_events': abi_decoded_events,
            'abi_decoded_transfers': abi_decoded_transfers,
        }
