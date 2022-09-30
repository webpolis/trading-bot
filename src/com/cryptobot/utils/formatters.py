import re


def format_str_as_number(number):
    return float(re.sub(r'[^\d\.]+', '', str(number)))
