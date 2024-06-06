# This script uses Selenium WebDriver to login to a website.
# Selenium is a popular tool for automating web browsers.

from selenium import webdriver

def login():
    # Create a new instance of the Chrome WebDriver
    driver = webdriver.Chrome()

    # Navigate to the login page
    driver.get('https://scrapingClub.com/exercise/basic_login/')

    # Find the field to enter the username
    # We use XPath to locate the field by its id
    name_field = driver.find_element('xpath', '//*[@id="id_name"]')

    # Enter the username
    name_field.send_keys('johnCarter')

    # Find the field to enter the password
    # We use XPath to locate the field by its id
    password_field = driver.find_element('xpath', '//*[@id="id_password"]')

    # Enter the password
    password_field.send_keys('Password@123')

    # Find the login button
    # We use XPath to locate the button by its position in the DOM
    login_button = driver.find_element('xpath', '/html/body/div[3]/div/div/div[1]/div[3]/form/button')

    # Click the login button
    login_button.click()

# Call the login function
login()




