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
    # regular expression pattern to extract the date of a review from its HTML source code.
    # This expression matches a date string in the format "Month Day, Year", where Month is a 3-letter abbreviation
    # for the month name (e.g. "Jan" for January), Day is a one- or two-digit number, and Year is a four-digit number.
    # the (?:uary)?, (?:ch)?, etc. parts make the optional letters in the month abbreviation optional.
    review_date_pattern = re.compile('\d{1,2} de (?:ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun('
                                     '?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:tiembre)?|oct(?:ubre)?|nov(?:iembre)?|dic('
                                     '?:embre)?) de \d{4}')

    # regular expression matches a URL for an Amazon product review page
    # The ^ character matches the beginning of the string, https: matches the literal string "https:"
    # \/{2} matches two forward slashes, www.amazon.com\/ matches the literal string "www.amazon.com/",
    product_name_pattern = re.compile('^https:\/{2}www.amazon.es\/(.+)\/product-reviews')

    def __init__(self):
        # Create a new requests Session object, which is used to make HTTP requests to the Amazon website
        self.session = requests.Session()
        # Define the browser that will make the request to the server
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ' \
                                             'like Gecko) Chrome/58.0.3029.110 Safari/537.3 '

        # Specify the MIME types that the client is willing to accept in the response.
        # The values in the header are listed in order of preference,
        # with a "q" parameter assigned to each value to indicate the degree of preference.
        # if not given, q=1 --> text/html is the same as text/html;q=1
        self.session.headers['Accept'] = 'text/html,application/xhtml+xml,image/webp,application/xml;q=0.9,*/*;q=0.8'

        # Specify the preferred language(s) for the response from the server. This tells you prefer Spanish (Spain)
        # as your first choice, and Spanish in general as your second choice with a lower priority (0.5).
        self.session.headers['Accept-Language'] = 'es-ES,es;q=0.5'

        # Specify whether the client wants to keep the connection open for further requests or close it after the
        # current request.
        self.session.headers['Connection'] = 'keep-alive'

        # Tell the server that the client would like to access a resource using a secure protocol, such as HTTPS.
        # When set to '1', it indicates that the client is willing to upgrade insecure requests to a secure
        # connection by following redirects from HTTP to HTTPS.
        self.session.headers['Upgrade-Insecure-Requests'] = '1'

    def scrapereviews(self, url, page_num, filter_by='recent'):
        """
        args
            filter_by: recent or helpful
        return
            namedtuple
        """
        # Try to extract the base URL from the input URL, and then modify it by adding the parameters for sorting
        # and filtering the reviews, as well as the page number to retrieve.
        try:
            # The regular expression '^.+(?=\/)' used in re.search matches any character (.) one or more times (
            # +) at the beginning of the string (^) until it finds a forward slash (\/) but doesn't include it in
            # the match because it uses a positive lookahead assertion ((?=\/)). Basically, it will return the
            # text until the penultimate '/'
            review_url = re.search('^.+(?=\/)', url).group()

            # The extracted base URL is then modified by adding the parameters for sorting (filter_by) and
            # filtering (reviewerType) the reviews, as well as the page number to retrieve (page_num). These
            # parameters are added to the end of the URL using string formatting.
            review_url = review_url + '?reviewerType=all_reviews&sortBy={0}&pageNumber={1}'.format(filter_by,
                                                                                                   page_num)
            print('Processing {0}...'.format(review_url))
            response = self.session.get(review_url)

            # The product_name_pattern regular expression is used to extract the product name from the URL. If
            # the URL does not match the pattern, the search method will return None, and the group(1) method
            # will raise an AttributeError. In that case, the code will print a message saying that the URL is
            # invalid and return from the method.
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
                review_title = product_review.find('a', {'data-hook': 'review-title'}).text.strip()  # .strip()
                # method removes any leading and trailing whitespace from the text content
                verified_purchase = True if product_review.find('span', {'data-hook': 'avp-badge'}) else False
                review_body = product_review.find('span', {'data-hook': 'review-body'}).text.strip()
                rating = product_review.find('i', {'data-hook': 'review-star-rating'}).text
                review_date = self.review_date_pattern.search(
                    product_review.find('span', {'data-hook': 'review-date'}).text).group(0)
                reviews.append(
                    review(product_name, review_title, review_body, rating, review_date,
                           verified_purchase))

            # Quit the webdriver and return the reviews
            driver.quit()
            return reviews

            # # The response.content contains the HTML code of the web page, and we are passing it to the
            # # BeautifulSoup constructor along with the 'html.parser' argument to create a BeautifulSoup object
            # # that can be used to parse and navigate the HTML code.
            # soup = BeautifulSoup(response.content, 'html.parser')
            # review_list = soup.find('div', {'id': 'cm_cr-review_list'})
            #
            # reviews = []
            # product_reviews = review_list.find_all('div', {'data-hook': 'review'})  # return reviews
            # for product_review in product_reviews:
            #     review_title = product_review.find('a', {'data-hook': 'review-title'}).text.strip()  # .strip()
            #     # method removes any leading and trailing whitespace from the text content
            #     verified_purchase = True if product_review.find('span', {'data-hook': 'avp-badge'}) else False
            #     review_body = product_review.find('span', {'data-hook': 'review-body'}).text.strip()
            #     rating = product_review.find('i', {'data-hook': 'review-star-rating'}).text
            #     review_date = self.review_date_pattern.search(
            #         product_review.find('span', {'data-hook': 'review-date'}).text).group(0)
            #     reviews.append(
            #         review(product_name, review_title, review_body, rating, review_date,
            #                verified_purchase))
            # return reviews

        except Exception as e:
            print(e)
            return None
