import time
import pandas as pd
from amzn_reviews import AmazonScraper
import tkinter as tk
from tkinter import simpledialog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv

reviews = []
amz_scraper = AmazonScraper()

# Ask user for product reviews URL
window_url = tk.Tk()
ROOT_url = tk.Tk()
ROOT_url.withdraw()
product_url = simpledialog.askstring(title="URL",
                                     prompt="Indicate the URL you want to get the reviews from:")

# Ask for the first page the user wants to get the reviews from
window_firstpage = tk.Tk()
ROOT_year = tk.Tk()
ROOT_year.withdraw()
first_page = int(simpledialog.askstring(title="First Page",
                                        prompt="Indicate the first page you want to scrap:"))

# Ask for the last page the user wants to get the reviews from
window_lastpage = tk.Tk()
ROOT_year = tk.Tk()
ROOT_year.withdraw()
last_page = int(simpledialog.askstring(title="Last Page",
                                       prompt="Indicate the last page you want to scrap:"))

for page_num in range(first_page, last_page):
    reviews.extend(amz_scraper.scrapereviews(url=product_url, page_num=page_num))
    time.sleep(1)

df = pd.DataFrame(reviews)
df.to_excel('amazon review {0}.xlsx'.format(reviews[0].product_name), index=False)

# Ask for the email where the user wants to receive the reviews file
window_mail = tk.Tk()
ROOT_year = tk.Tk()
ROOT_year.withdraw()
user_email = simpledialog.askstring(title="Email",
                                    prompt="Indicate the email where you want to receive the reviews file:")

# Send email with the file output
sender_email = 'MY_EMAIL'

# SMTP server settings for Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # or 465 if using SSL/TLS

# Login credentials
load_dotenv('variables.env')
username = os.getenv('MY_EMAIL')
password = os.getenv('MY_PASSWORD')
print(username)

# Excel file to attach
file_path = 'amazon review {0}.xlsx'.format(reviews[0].product_name)

# Create a multipart message container and set the recipients, subject, and body
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = user_email
msg['Subject'] = 'Your Amazon product reviews file'

# Add a text body
body = 'Please find the attached Excel file with the reviews of the product "{0}" ' \
       'that you requested.'.format(reviews[0].product_name)
msg.attach(MIMEText(body, 'plain'))

# Add the Excel file as an attachment
with open(file_path, 'rb') as f:
    excel_file = MIMEApplication(f.read(), _subtype='xlsx')
    excel_file.add_header('content-disposition', 'attachment', filename=f.name)
msg.attach(excel_file)

# Create a secure SSL/TLS connection and login to the SMTP server
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(username, password)
    server.sendmail(sender_email, user_email, msg.as_string())
    print('Email sent successfully')
