from selenium import webdriver

from com.cryptobot.config import Config


def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--disable-dev-shm-using")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-infobars")

    return webdriver.Chrome(
        Config().get_settings().selenium.chromedriver_path, chrome_options=chrome_options)
