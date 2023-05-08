import re
from collections import namedtuple
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

review = namedtuple('review', ['product_name', 'review_title', 'comment', 'rating', 'date',
                               'verified_purchase'])


class AmazonScraper:
    review_date_pattern = re.compile('\d{1,2} de (?:ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun('
                                     '?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:tiembre)?|oct(?:ubre)?|nov(?:iembre)?|dic('
                                     '?:embre)?) de \d{4}')
    product_name_pattern = re.compile('^https:\/{2}www.amazon.es\/(.+)\/product-reviews')

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ' \
                                             'like Gecko) Chrome/58.0.3029.110 Safari/537.3 '
        self.session.headers['Accept'] = 'text/html,application/xhtml+xml,image/webp,application/xml;q=0.9,*/*;q=0.8'
        self.session.headers['Accept-Language'] = 'es-ES,es;q=0.5'
        self.session.headers['Connection'] = 'keep-alive'
        self.session.headers['Upgrade-Insecure-Requests'] = '1'

    def scrapereviews(self, url, page_num, filter_by='recent'):
        """
        args
            filter_by: recent or helpful
        return
            namedtuple
        """
        try:
            review_url = re.search('^.+(?=\/)', url).group()
            review_url = review_url + '?reviewerType=all_reviews&sortBy={0}&pageNumber={1}'.format(filter_by,
                                                                                                   page_num)
            print('Processing {0}...'.format(review_url))
            response = self.session.get(review_url)
            product_name = self.product_name_pattern.search(url).group(1) if self.product_name_pattern.search(
                url) else ''
            if not product_name:
                print('url is invalid. Please check the url.')
                return
            else:
                product_name = product_name.replace('-', ' ').replace('%C3%A1', 'á').replace('%C3%A9', 'é')\
                    .replace('%C3%AD', 'í').replace('%C3%B3', 'ó').replace('%C3%BA', 'ú').replace('%C3%B1', 'ñ')

            # Driver Options Configuration
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-notifications')  # disable pop-ups
            options.add_argument('start-maximized')  # starts maximized

            # Create a webdriver instance and navigate to the review URL
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
            driver.get(review_url)
            driver.get(review_url)

            driver.find_element('xpath', '//*[@id="sp-cc-rejectall-link"]').click()

            # Wait for the review section to load dynamically
            wait = WebDriverWait(driver, 10)
            review_list = driver.find_element('xpath', '//*[@id="cm_cr-review_list"]')

            # Use BeautifulSoup to parse the page source
            review_to_html = review_list.get_attribute('innerHTML')
            soup = BeautifulSoup(review_to_html, 'html.parser')

            # Extract the individual reviews
            reviews = []
            product_reviews = soup.find_all('div', {'data-hook': 'review'})  # return reviews
            for product_review in product_reviews:
                review_title = product_review.find('a', {'data-hook': 'review-title'}).text.strip() 
                verified_purchase = True if product_review.find('span', {'data-hook': 'avp-badge'}) else False
                review_body = product_review.find('span', {'data-hook': 'review-body'}).text.strip()
                rating = product_review.find('i', {'data-hook': 'review-star-rating'}).text
                review_date = self.review_date_pattern.search(
                    product_review.find('span', {'data-hook': 'review-date'}).text).group(0)
                reviews.append(
                    review(product_name, review_title, review_body, rating, review_date,
                           verified_purchase))

            driver.quit()
            return reviews


        except Exception as e:
            print(e)
            return None
