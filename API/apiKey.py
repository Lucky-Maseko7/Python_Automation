import requests
baseUrl = 'http://api.openweathermap.org/data/2.5/forecast'
parameters = {'appid': 'a03d0d65b881af4e867ca1a058d0e69e','q': 'Roodepoort,ZA'}
response = requests.get(baseUrl, params=parameters)
print(response.content)
