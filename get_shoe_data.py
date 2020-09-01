import re
import requests
from bs4 import BeautifulSoup
import time

# Get all shoes
brooks = requests.get('https://www.brooksrunning.com/en_us/shoes/?&sz=300')
bs = BeautifulSoup(brooks.text, 'html.parser')

# Get links to details for all shoes
products = bs.find_all('div', {'class': re.compile('.*product-container.*')})

product_links = []

for product in products:
    product_links.append(product.find('a')['href'])


def get_shoe_specs(shoe_url):
    """
    Get the specs for a brooks shoe

    Args:
        shoe_url (str): the url to the shoe product/details page

    Returns:
        dict: returns the specs of the shoe
    """
    # Request page
    shoe_page = requests.get(product_link)
    shoe_parsed = BeautifulSoup(shoe_page.text, 'html.parser')

    # Retrieve specs from specs table
    shoe_spec_rows = shoe_parsed.find_all('tr', {'class': 'specs__row'})

    # Loop through each spec
    features = {}
    for spec_row in shoe_spec_rows:
        feature = spec_row.td.text
        value = spec_row.p.text
        features[feature] = value

    return features


# Retrieve details for each product
for product_link in product_links:
    shoe_features = get_shoe_specs(product_link)
    print(product_link)
    print(shoe_features)
    time.sleep(1)
