import re
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# Get all shoes
brooks = requests.get('https://www.brooksrunning.com/en_us/shoes/?&sz=300')
bs = BeautifulSoup(brooks.text, 'html.parser')

# Get links to details for all shoes
products = bs.find_all('div', {'class': re.compile('.*product-container.*')})

product_links = []

for product in products:
    product_links.append(product.find('a')['href'])

def get_shoe_page(shoe_url):
    shoe_page = requests.get(product_link)
    return BeautifulSoup(shoe_page.text, 'html.parser')


def get_shoe_name(shoe_page):
    """
    Get the name of the shoe

    Args:
        shoe_page (obj): The shoe page as parsed by get_shoe_page function

    Returns:
        str: returns the name of the shoe
    """
    return shoe_page.find(re.compile('.*'), {'class': re.compile('product--meta__title.*')}).text


def get_shoe_type(shoe_page):
    """
    Get the type of shoe

    Args:
        shoe_page (obj): The shoe page as parsed by get_shoe_page function

    Returns:
        str: returns the type of shoe
    """
    try:
        return shoe_page.find(re.compile('.*'), {'class': re.compile('product--meta__sub-title.*')}).text
    except AttributeError:
        return None


def get_shoe_price(shoe_page):
    """
    Get the price of the shoe

    Args:
        shoe_page (obj): The shoe page as parsed by get_shoe_page function

    Returns:
        str: returns the price of the shoe
    """
    try:
        price = shoe_page.find(re.compile('.*'), {'class': re.compile('product--meta__price.*')}).text
        return price
    except AttributeError:
        return None



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


# Retrieve details for each product
all_shoes = list()
loops = 0
# loop_max = 9
for product_link in product_links:
    shoe_page = get_shoe_page(product_link)
    shoe_features = get_shoe_specs(shoe_page)
    shoe_features['name'] = get_shoe_name(shoe_page)
    shoe_features['price'] = get_shoe_price(shoe_page)
    shoe_features['type'] = get_shoe_type(shoe_page)
    shoe_details = pd.DataFrame(shoe_features, index=[shoe_features['name']])
    all_shoes.append(shoe_details)
    time.sleep(1)
    loops += 1
    # if loops > loop_max:
    #    break
    print(str(loops), ' of', str(len(product_links)))


all_shoes = pd.concat(all_shoes)
all_shoes.to_csv('shoe_details.csv')
