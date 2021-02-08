import os
import re
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from threading import Thread
from bs4 import BeautifulSoup
# App
from app.utils import response_json
from app.utils.env_constants import ENV_CONTEXT, WEBDRIVER, YAHOO_URL, MINIMAL_HOLD

chrome_options = Options()

if ENV_CONTEXT in os.environ:
    DRIVER_PATH = os.environ[WEBDRIVER]
    YAHOO_URL = os.environ[YAHOO_URL]
    MINIMAL_HOLD = float(os.environ[MINIMAL_HOLD])
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
else:
    DRIVER_PATH = '/home/tl/code/serasa_crawler/app/utils/chromedriver'
    YAHOO_URL = 'https://finance.yahoo.com/screener/new'
    MINIMAL_HOLD = 1
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')


class YahooStocks:
    def __init__(self, region):
        self.driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
        self.url = YAHOO_URL
        self.region = region
        self.payload_return = dict()

    @staticmethod
    def normalize_text(text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = text.strip()
        text = text.replace(' ', '-')
        return text

    def find_by_text_and_click(self, tag_name, text, prop=None, hold=None):
        norm_text = self.normalize_text(text)
        tags = self.driver.find_elements_by_tag_name(tag_name)

        found_clickable_element = False
        for tag in tags:
            if prop:
                if self.normalize_text(tag.get_property(prop)) == norm_text:
                    found_clickable_element = True
            else:
                if self.normalize_text(tag.text) == norm_text:
                    found_clickable_element = True

            if found_clickable_element:
                self.driver.execute_script(f"window.scrollTo(0, {tag.location['y']-200});")
                tag.click()
                sleep(MINIMAL_HOLD if not hold else hold)
                return

        self.driver.close()
        raise Exception(f"Can't find a tag <{tag_name}> "
                        f"with {'property' if prop else 'text'}: "
                        f"{text} to click.")

    def is_button_enable(self, text):
        norm_text = self.normalize_text(text)
        buttons = self.driver.find_elements_by_tag_name('button')
        for button in buttons:
            if self.normalize_text(button.text) == norm_text:
                return not button.get_property('disabled')
        raise Exception(f"Can't find a tag <button> "
                        f"with 'text': {text} to check if it enable.")

    @staticmethod
    def process_table(url, return_payload):
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'lxml')
        keys = {'Symbol', 'Name', 'Price(Intraday)'}
        information_length = 0

        # go through tables
        for t in soup.find_all('table'):
            use_table = False
            ths = t.find_all('th')
            for th in ths:
                if th.text in keys:
                    information_length += 1
                if information_length == len(keys)-1:
                    use_table = True
                    break
            if use_table:
                for tr in t.find_all('tr'):
                    stock_fields = ["symbol", "name", "price"]
                    symbol = None
                    for i, td in enumerate(tr.find_all('td')):
                        if i == 3:
                            break
                        if i == 0:
                            symbol = td.text
                            return_payload[symbol] = dict()
                        return_payload[symbol][stock_fields[i]] = td.text
        return return_payload

    def get_regions_list(self):
        response_content = list()
        try:
            self.driver.get(self.url)

            # remove default region
            self.find_by_text_and_click('button', 'Remove United States', prop='title')

            # add region
            self.find_by_text_and_click('span', "Add Region")
            menu = self.driver.find_elements_by_id("dropdown-menu")
            ul_menu = None
            for m in menu:
                try:
                    ul_menu = m.find_element_by_tag_name('ul')
                except NoSuchElementException:
                    pass

            if ul_menu is None:
                raise Exception("Can't find List of Regions")

            for reg in ul_menu.find_elements_by_tag_name('span'):
                reg = self.normalize_text(reg.text)
                response_content.append(reg)

            response_content = sorted(response_content)
        except Exception as error:
            return response_json({
                    "error_type": str(type(error)),
                    "error": str(error)})

        return response_json(response_content)

    def get_stocks_by_region(self):
        response_content = dict()
        try:
            self.driver.get(self.url)

            # remove default region
            self.find_by_text_and_click('button', 'Remove United States', prop='title')

            # add region
            self.find_by_text_and_click('span', "Add Region")
            self.find_by_text_and_click('span', self.region)

            estimated_results_is_next = False
            number_of_threads = None
            for div in self.driver.find_elements_by_tag_name('div'):
                if estimated_results_is_next:
                    number_of_threads = int(int(div.text) / 100)
                    break
                if self.normalize_text(div.text) == self.normalize_text("Estimated results"):
                    estimated_results_is_next = True
            if number_of_threads is None:
                raise Exception("pager is broken")

            self.find_by_text_and_click('button', "Find Stocks", hold=2)
            pager_url = str(self.driver.current_url).replace("offset=0&count=25", "")
            self.driver.close()

            threads = list()
            for t_index in range(0, number_of_threads+1):
                url = f"{pager_url}&offset={t_index*100}&count=100"
                t = Thread(target=self.process_table, args=(url, response_content))
                threads.append(t)

            [t.start() for t in threads]
            [t.join() for t in threads]

            response_content = dict(sorted(response_content.items()))
        except Exception as error:
            return response_json({
                    "error_type": str(type(error)),
                    "error": str(error)})

        return response_json(response_content)
