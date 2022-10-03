import re

from com.cryptobot.schemas.tx import Tx


def format_str_as_number(number):
    return float(re.sub(r'[^\d\.]+', '', str(number)))


def tx_parse(tx):
    parsed_tx = {key: tx[key] for key in tx.keys()
                 & {'blockNumber', 'hash', 'from', 'to', 'gas', 'gasPrice', 'value'}}

    return Tx(
        parsed_tx['blockNumber'],
        parsed_tx['hash'],
        parsed_tx['from'],
        parsed_tx['to'],
        parsed_tx['gas'],
        parsed_tx['gasPrice'],
        parsed_tx['value']
    )
