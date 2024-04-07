import requests
from bs4 import BeautifulSoup
url = 'https://www.fctables.com/h2h/liverpool/manchester-united/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
quotes = soup.find_all('table', class_='table table-striped table-hover')
# statQuotes = quotes.find_all('')

for i in range(0, len(quotes)):
    statQuotes = quotes[i].find_all('tr')
    for j in range(0, len(statQuotes)):
        print(statQuotes[j].text)
