import re
import requests
from bs4 import BeautifulSoup

brooks = requests.get('https://www.brooksrunning.com/en_us/shoes/')
bs = BeautifulSoup(brooks.text, 'html.parser')

print(bs.find_all('div',{'class':re.compile('.*product-container.*')}) )