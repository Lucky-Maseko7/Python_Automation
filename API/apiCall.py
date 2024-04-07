import requests
import json
baseUrl = 'https://api.upcitemdb.com/prod/trial/lookup'
# parameters = {'upc': '0012993441012'}
parameters = {'upc': '073366118238'}
response = requests.get(baseUrl, params=parameters)
print(response.url)
content = response.content
info = json.loads(content)
print(type(info))
print(info)
items = info['items']
itemInfo = items[0]
title = itemInfo['title']
brand = itemInfo['brand']
print(title)
print(brand)