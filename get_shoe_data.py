"""
Scrape running shoe information

This module contains code for web scrapping data about running shoes from the Brooks web page and writing the data to a csv

Attributes:
    detail_expressions (dict):
        Contains instructions/expressions for extracting various product details
"""

import re
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

detail_expressions = {
    'Name': 'product--meta__title.*',
    'Price': 'product--meta__price.*',
    'Type': 'product--meta__sub-title.*'
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
        shoe_page (obj): The shoe page as parsed by get_page function

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


def get_all_shoe_links(url):
    """
    Retrieve all the links to individual shoe detail pages from the browse products page

    Args:
        url (str): The url of the browse products page

    Returns:
        list: List of links to each shoe
    """
    # Get all shoes
    bs = get_page(url)

    # Get links to details for all shoes
    products = bs.find_all('div', {'class': re.compile('.*product-container.*')})

    product_links = []

    for product in products:
        product_links.append(product.find('a')['href'])

    return product_links


# 999 shoes would likely be an error, lets not put an infinite loop against their server
def get_all_shoes(max_loops=999, output=True):
    product_links = get_all_shoe_links('https://www.brooksrunning.com/en_us/shoes/?&sz=300')

    # setup looping variables
    all_shoes = list()
    loops = 0

    for product_link in product_links:
        shoe_page = get_page(product_link)

        # extract shoe details
        shoe_features = get_shoe_specs(shoe_page)
        for detail in detail_expressions:
            shoe_features[detail] = get_detail(shoe_page, detail_expressions[detail])

        # setup as DataFrame and place with rest of shoes
        shoe_details = pd.DataFrame(shoe_features, index=[shoe_features['Name']])
        all_shoes.append(shoe_details)

        # pause in order to prevent taxing server
        time.sleep(1)

        # looping info and stops
        loops += 1
        if loops > max_loops:
            break
        print(str(loops), ' of', str(len(product_links)))

    all_shoes = pd.concat(all_shoes)

    # output data
    if output:
        all_shoes.to_csv('shoe_details.csv')
    else:
        print(all_shoes)


def main(max_shoes_retrieve, output_data):
    get_all_shoes(max_shoes_retrieve, output_data)


if __name__ == "__main__":
    main(int(input('Enter the number of shoes to retrieve: ')), bool(input('Do you want to output to a csv file: ')))
