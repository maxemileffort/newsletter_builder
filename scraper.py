
# borrowed from another repo: https://github.com/zero-to-mastery/breads-server
import requests, re, json, os, time, sys
from urllib.parse import unquote
from dotenv import load_dotenv
from fake_useragent import UserAgent, FakeUserAgentError
from goose3 import Goose
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
from random import seed, random, choice
from collections import Counter
from string import punctuation

load_dotenv()

link_preview = os.getenv('LINK_PREVIEW_KEY')

class Scraper:
    def __init__(self, url):
        self.url = url
        self.is_pdf = False
        self.reading = ''
        self.title = ''
        self.description = ''
        self.word_count = 0
        self.image = ''
        self.domain = ''
        self.headers = ''
        self.useragent = ''
        self.errors = []

    @classmethod
    def transform_url(cls, url_str):
        try:
            r = requests.get(url_str, timeout=10)
            if r.status_code != 404:
                return cls(url_str)
        except:
            pass
        
        url = unquote(url_str).replace(" ", "%20")
        if not re.match(r"http", url):
            url = "https://" + url.lstrip("www.")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 404:
                return cls(url)
        except:
            pass
        return ["Invalid URL.", "", "", "", 0, url_str]

    def useragent_generator(self):
        ua_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        fallback = choice(ua_list)
        try:
            ua = UserAgent(fallback=fallback)
            self.useragent = str(ua.random)
        except FakeUserAgentError:
            self.useragent = fallback
        return self.useragent

    def get_domain(self):
        try:
            self.domain = re.search(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]', self.url).group()
        except:
            self.domain = 'Unable to get domain'
            self.errors.append(sys.exc_info())
        return self.domain

    def check_if_pdf(self):
        self.is_pdf = bool(re.findall(r".pdf", self.url, flags=re.IGNORECASE))
        return self.is_pdf

    def build_headers(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cache-Control': 'no-cache',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': "https://www.google.com/search",
            'User-Agent': self.useragent,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
        }
        return self.headers

    def get_reading_data(self):
        g = Goose({'http_headers': self.headers})
        try:
            self.reading = g.extract(url=self.url)
        except:
            self.reading = ''

        if not self.reading or not self.reading.title or '403 Forbidden' in self.reading.title or self.reading.title == "Bloomberg":
            cached_url = 'https://webcache.googleusercontent.com/search?q=cache:' + self.url
            try:
                self.reading = g.extract(url=cached_url)
            except:
                self.reading = ''

        if not self.reading or 'Not Found' in self.reading.title or '404' in self.reading.title:
            r = requests.get(f'http://api.linkpreview.net/?key={link_preview}&q={self.url}')
            j = r.json()
            self.title, self.description, self.image = j['title'], j['description'], j['image']

    def get_title(self):
        if self.reading and not self.title:
            try:
                if 'title' in self.reading.opengraph:
                    self.title = self.reading.opengraph['title']
                elif self.reading.title:
                    self.title = self.reading.title
                if 'description' in self.reading.opengraph:
                    self.description = self.reading.opengraph['description']
                elif self.reading.meta_description:
                    self.description = self.reading.meta_description
                if not self.description and self.reading.cleaned_text:
                    self.description = self.reading.cleaned_text[:497] + '...'
                if 'image' in self.reading.opengraph:
                    self.image = self.reading.opengraph['image']
                elif self.reading.top_image:
                    self.image = self.reading.top_image
            except:
                self.title = "Unable to get title of article"

    def get_word_count(self):
        try:
            self.word_count = len(self.reading.cleaned_text.split()) if self.reading else 0
        except:
            self.word_count = 0
            self.errors.append(sys.exc_info())

    def auto_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        browser = Browser('chrome', service=Service(ChromeDriverManager().install()), headless=False, options=options)
        browser.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        time.sleep(random() * 10 + 1)

        try:
            browser.visit(self.url)
        except:
            self.title, self.description, self.image, self.word_count, self.domain = '', '', '', 0, ''
            return

        if browser.is_element_present_by_id("rc-anchor-container", wait_time=5):
            browser.quit()
            self.reading, self.title, self.description, self.image, self.word_count = '', "", "Content retrieval issue. Retrying...", "", 0
            return
        
        self.simulate_scrolling(browser)

        html = browser.html
        browser.quit()
        soup = BeautifulSoup(html, "lxml")
        self.extract_html_data(soup)

    def simulate_scrolling(self, browser):
        time.sleep(random() * 10 + 2)
        for element in ['main', '#main', '.main', 'footer', '#footer', '.footer', 'header', '#header', '.header']:
            try:
                browser.execute_script(f"var elem = document.querySelector('{element}'); if(elem){{elem.scrollIntoView({{behavior: 'smooth', block: 'center'}})}};")
            except:
                pass
            time.sleep(random() * 10 + 2)

    def extract_html_data(self, soup):
        try:
            self.title = soup.find("meta", property="og:title")['content'] or soup.title.string.strip() or "Unable to get title"
        except:
            self.title = "Unable to get title"

        try:
            self.description = soup.find("meta", property="og:description")['content'] or " ".join(p.getText() for p in soup.findAll('p'))[:147] + '...'
        except:
            self.description = "Unable to get description"

        try:
            self.image = soup.find("meta", property="og:image")['content'] or soup.find("img")['src'] or ''
        except:
            self.image = ''

        text_p = (''.join(s.findAll(text=True)) for s in soup.findAll('p'))
        c_p = Counter((x.rstrip(punctuation).lower() for y in text_p for x in y.split()))
        self.word_count = sum(c_p.values())

if __name__ == "__main__":


    BASE_URL = sys.argv[1]
    base_scrape = Scraper.transform_url(BASE_URL)
    if isinstance(base_scrape, list):
        print(json.dumps(base_scrape))
        sys.exit()

    if base_scrape.check_if_pdf():
        sys.exit()

    base_scrape.useragent_generator()
    base_scrape.build_headers()
    base_scrape.get_domain()
    base_scrape.get_reading_data()
    base_scrape.get_title()
    base_scrape.get_word_count()

    if 'Unable to get title of article' in base_scrape.title:
        time.sleep(60)
        base_scrape.auto_browser()

    values = [base_scrape.title, base_scrape.domain, base_scrape.description, base_scrape.image, base_scrape.word_count, BASE_URL.strip()]
    print(json.dumps(values))
