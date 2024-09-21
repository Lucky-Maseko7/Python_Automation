from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Path to your ChromeDriver
driver_path = r'C:\Windows\System32\chromedriver-win64\chromedriver.exe'

# Initialize the Service object with the path to the ChromeDriver
service = Service(driver_path)

# Initialize the WebDriver with the service
driver = webdriver.Chrome(service=service)

# # Initialize the WebDriver (Chrome in this case)
# driver = webdriver.Chrome(executable_path=driver_path)

# URL of the website you want to scrape
url = "https://understat.com/league/La_liga/2024"

# Open the webpage
driver.get(url)

# Wait for the page to load completely (you can adjust the time or use explicit waits)
time.sleep(15)

# Wait for the radio button to be visible
try:
    # radio_button = WebDriverWait(driver, 30).until(
    #     EC.visibility_of_element_located((By.ID, "home-away2"))
    # )

    # # Optionally scroll into view
    # driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)

    # # Optionally wait until it is clickable
    radio_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, "home-away2"))
    )

    # Click the radio button
    # radio_button.click()

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()

# Allow some time for the page to refresh/load the new content
time.sleep(2)

# Extract the HTML of the page after the radio button click
page_source = driver.page_source

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Find the table inside the div with the specified ID
table_div = soup.find('div', id='league-chemp', class_='chemp margin-top jTable')

# If the table exists, extract it
if table_div:
    table = table_div.find('table')  # Assuming there's a table inside this div
    if table:
        # Print the table or extract its data
        print(table.prettify())
    else:
        print("No table found in the specified div.")
else:
    print("Div not found.")

# Close the browser
driver.quit()
