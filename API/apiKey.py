import json
import requests



def get_weather_data(city, country):
    """
    Get weather data for a given city and country

    Args:
        city (str): The name of the city
        country (str): The country code of the city

    Returns:
        dict: The weather data as a dictionary
    """
    # Define the base URL for the OpenWeatherMap API
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    
    # Define the parameters for the API request
    params = {
        'appid': 'a03d0d65b881af4e867ca1a058d0e69e',
        'q': f'{city},{country}'
    }
    
    # Send a GET request to the API and retrieve the response
    response = requests.get(base_url, params=params)
    
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Return the weather data as a dictionary
    return response.json()


if __name__ == '__main__':
    # Set the city and country for which to get the weather data
    city = 'Roodepoort'
    country = 'ZA'
    
    # Get the weather data for the specified city and country
    weather_data = get_weather_data(city, country)
    
    # Print the weather data as a formatted JSON string
    print(json.dumps(weather_data, indent=4))
    
# Print the contents of the response (should be None)
print(json.dumps(weather_data, indent=4))
