import re


def format_str_as_number(number):
    return float(re.sub(r'[^\d\.]+', '', str(number)))


def tx_parse(tx):
    return {key: tx[key] for key in tx.keys()
            & {'blockNumber', 'hash', 'from', 'to', 'gas', 'gasPrice', 'value'}}
