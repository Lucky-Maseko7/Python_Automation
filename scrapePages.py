from bs4 import BeautifulSoup
import requests
url = 'https://scrapingclub.com/exercise/list_basic/?page=1'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
items = soup.find_all('div', class_='w-full rounded border')
count = 1
for i in items:
    itemName = i.find('h4').text.strip('\n')
    itemPrice = i.find('h5').text
    print('%s ) Price: %s, Item Name %s' % (count, itemPrice, itemName))
    count += 1
# pages = soup.find_all('nav', class_='pagination')
links = []
urls = soup.find_all('span', class_='page')
for url in urls:
    if(url.find('a') != None):
        print(url.find('a').text)
        x = url.find('a')
