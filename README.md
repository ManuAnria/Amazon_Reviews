# ***Amazon_Reviews***
Scrapper for products reviews in **Amazon Spain**

## Amazon Review Scraper and Emailer
This project includes two Python programs: amzn_reviews.py and demo_reviews.py.
### amzn_reviews.py
This program creates a class named AmazonScraper to extract reviews from the specified URL. 

It will scrap the product name, the review title, the comments, rating and purchase date,  along with a Boolean that indicates whether the purchase was verified or not.
### demo_reviews.py
To run the program, simply execute the demo_reviews.py file and follow the prompts. You will be asked to enter **the URL of the main page of the reviews of the product** you want to scrape reviews for, as well as the first and last pages you want to scrape.

Here is an example of the URL the user should provide: https://www.amazon.es/echo-dot-2022/product-reviews/B09B8X9RGM/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews

In order to get to this URL, click on the reviews of the product, and then click "See all reviews".

Once the program has finished scraping the reviews, it will save them to an Excel file in the same directory as the program. The name of the file will include the name of the product you scraped reviews for.

This program allows you to receive an email with the Excel file containing the reviews that you scraped using this program. 

You will be asked to enter the email address of the recipient.

Once the program has established a connection to the email server and sent the email, it will display a success message in the console.
## Prerequisites
To use these programs, you will need to have the following software installed on your computer:

•	Python 3.10.8 or higher

•	The Python libraries included in the requirements.txt file
