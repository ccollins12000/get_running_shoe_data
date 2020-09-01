import re
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

detail_expressions = {
    'Name': 'product--meta__title.*',
    'Price': 'product--meta__price.*',
    'Type':  'product--meta__sub-title.*'
}


def get_detail(shoe_page, expression):
    """
    Get a specific detail about the shoe

    Args:
        shoe_page (obj): The shoe page as parsed by get_shoe_page function
        expression (str): Regular expression for value of HTML element class

    Returns:
        str: returns the detail about the shoe
    """
    try:
        price = shoe_page.find(re.compile('.*'), {'class': re.compile(expression)}).text
        return price
    except AttributeError:
        return None


def get_page(page_url):
    """
    Retrieve and parse a web page

    Args:
        page_url (str): The url of the page to retrieve and parse

    Returns:
        obj: Beautiful Soup html object from parse page. If the page cannot be retrieved nothing is returned
    """
    try:
        page = requests.get(page_url)
    except requests.exceptions.RequestException:
        return None
    return BeautifulSoup(page.text, 'html.parser')


def get_shoe_specs(shoe_page):
    """
    Get the specs for a brooks shoe

    Args:
        shoe_page (obj): The shoe page as parsed by get_shoe_page function

    Returns:
        dict: returns the specs of the shoe
    """
    # Retrieve specs from specs table
    try:
        shoe_spec_rows = shoe_page.find_all('tr', {'class': 'specs__row'})
    except AttributeError:
        return {'sepcs': 'no specs'}

    # Loop through each spec
    features = {}
    for spec_row in shoe_spec_rows:
        feature = spec_row.td.text
        value = spec_row.p.text
        features[feature] = value

    return features


# Get all shoes
bs = get_page('https://www.brooksrunning.com/en_us/shoes/?&sz=300')

# Get links to details for all shoes
products = bs.find_all('div', {'class': re.compile('.*product-container.*')})

product_links = []

for product in products:
    product_links.append(product.find('a')['href'])


# Retrieve details for each product
all_shoes = list()
loops = 0
loop_max = 2
for product_link in product_links:
    shoe_page = get_page(product_link)
    shoe_features = get_shoe_specs(shoe_page)
    for detail in detail_expressions:
        shoe_features[detail] = get_detail(shoe_page, detail_expressions[detail])
    shoe_details = pd.DataFrame(shoe_features, index=[shoe_features['Name']])
    all_shoes.append(shoe_details)
    time.sleep(1)
    loops += 1
    if loops > loop_max:
        break
    print(str(loops), ' of', str(len(product_links)))


all_shoes = pd.concat(all_shoes)
print(all_shoes)
# all_shoes.to_csv('shoe_details.csv')
