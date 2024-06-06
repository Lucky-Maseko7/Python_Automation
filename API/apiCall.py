import requests


# Define a function that makes an API call to the UPC item database
# and returns the title and brand of the item with the given UPC code.
def api_call(upc):
    # Set the base URL for the API request
    base_url = 'https://api.upcitemdb.com/prod/trial/lookup'
    # Send a GET request to the API with the UPC code as a parameter
    response = requests.get(base_url, params={'upc': upc})
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    # Parse the JSON response into a Python dictionary
    data = response.json()
    # Get the list of items from the response
    items = data['items']
    # If there is at least one item, return its title and brand
    if items:
        item_info = items[0]
        return item_info['title'], item_info['brand']
    # If there are no items, return None for both title and brand
    return None, None


if __name__ == '__main__':
    # Set the UPC code for the item we want to look up
    upc = '073366118238'
    # Call the api_call function with the UPC code
    title, brand = api_call(upc)
    # Print the title and brand of the item
    print(title)
    print(brand)

