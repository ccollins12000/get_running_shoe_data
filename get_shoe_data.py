import re
import requests
from bs4 import BeautifulSoup
import time

# Get all shoes
brooks = requests.get('https://www.brooksrunning.com/en_us/shoes/?&sz=300')
bs = BeautifulSoup(brooks.text, 'html.parser')

# Get links to details for all shoes
products = bs.find_all('div',{'class':re.compile('.*product-container.*')})

product_links = []

for product in products:
    product_links.append(product.find('a')['href'])

# Retrieve details for each product
for product_link in product_links:
    product_page = requests.get(product_link)
    bs = BeautifulSoup(product_page.text, 'html.parser')
    spec_rows = bs.find_all('tr',{'class':'specs__row'})
    features = {}
    for spec_row in spec_rows:
        feature = spec_row.td.text
        value = spec_row.p.text
        features[feature] = value

    print(product_page)
    print(features)
    time.sleep(1)

