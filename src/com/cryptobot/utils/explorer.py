import logging
import re
import requests
from threading import RLock
from backoff import expo, on_exception
from bs4 import BeautifulSoup
from com.cryptobot.config import Config
from com.cryptobot.utils.logger import PrettyLogger
from com.cryptobot.utils.network import ProviderNetwork, get_current_network
from com.cryptobot.utils.request import HttpRequest
from ratelimit import RateLimitException, limits

lock = RLock()
request = HttpRequest()
settings = Config().get_settings()
max_threads = settings.runtime.classifiers.SwapClassifier.max_concurrent_threads
max_calls = int(300/max_threads)
period_per_thread = int(30/max_threads)
network = get_current_network()


@on_exception(expo, RateLimitException, max_tries=3, max_time=10)
@limits(calls=max_calls, period=period_per_thread)
def get_token_info(address):
    global lock
    global network

    with lock:
        response = request.get(
            settings.endpoints.etherscan.token.format(address=address), raw=True)
        soup = BeautifulSoup(response, "html.parser")
        overview = soup.find('div', {'id': 'ContentPlaceHolder1_tr_valuepertoken'})

        if overview == None:
            return None

        if network != ProviderNetwork.ETHEREUM:
            overview_clr = re.sub(r'[\r\n]+', '', overview.text.strip(),
                                  flags=re.MULTILINE | re.IGNORECASE)
            market_cap = re.sub(r'.*Market Cap[\s\t\n\r]*\$([\d\.\,]+).*$',
                                '\\1', overview_clr, flags=re.MULTILINE | re.IGNORECASE)
            market_cap = float(market_cap.replace(',', ''))
        else:
            overview_clr = overview.text.strip()
            market_cap = float(
                re.sub(r'[^\.\d]+', '', list(overview.next_siblings)[1].text.strip()))

        price_usd = re.sub(r'.*Price[\s\t]*\$([\d\.\,]+).*$',
                           '\\1', overview_clr, flags=re.MULTILINE | re.IGNORECASE)
        price_usd = float(price_usd.replace(',', ''))

        return {
            'address': address,
            'name': None,
            'symbol': None,
            'decimals': None,
            'price_usd': price_usd,
            'market_cap': market_cap
        }


def get_tokens_by_page(page_num, selenium_driver):
    tokens = []
    url = f'{settings.endpoints.etherscan.tokens}?ps=100&p={page_num}'

    try:
        selenium_driver.get(url)
    except Exception as error:
        print(error)

    soup = BeautifulSoup(selenium_driver.page_source, 'html.parser')
    tokens_table = soup.find('table', {'id': 'tblResult'})
    rows = tokens_table.find('tbody').find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        link = cols[1].find('a')
        symbol = re.sub(r'.*\(([\w]+)\)$', '\\1', link.text.strip())
        price = float(re.sub(r'[^\d\.]+', '', cols[2].find('span').text.strip()))
        market_cap = re.sub(r'[^\d\.]+', '', cols[5].text.strip())
        market_cap = float(market_cap) if market_cap != '' else None
        address = link.attrs['href'].split('/')[-1]
        token = {'symbol': symbol, 'address': address,
                 'price': price, 'market_cap': market_cap}

        tokens.append(token)

    return tokens


explorer_logger = PrettyLogger(HttpRequest.__name__, logging.INFO)
