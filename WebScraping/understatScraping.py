from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import logging
# import tensorflow as tf
from selenium.webdriver.chrome.service import Service

# # Disable XNNPACK delegate if required
# interpreter = tf.lite.Interpreter(model_path="your_model.tflite", experimental_preserve_all_tensors=True)
# interpreter.modify_graph_with_delegate(None)  # Disable problematic delegate

# logging.basicConfig(level=logging.DEBUG)
# Set Chrome options to run in headless mode
from selenium.webdriver.chrome.options import Options

# Path to your ChromeDriver
driver_path = 'C:\Windows\System32\chromedriver-win64\chromedriver.exe'

# Initialize the Service object with the path to the ChromeDriver
service = Service(driver_path)

# Initialize the WebDriver with the service
driver = webdriver.Chrome(service=service)

# Navigate to the web page
url = "https://understat.com/league/La_liga/2024"  # Replace with actual URL
driver.get(url)

# Wait for page load and elements
wait = WebDriverWait(driver, 30)  # Increase wait time to 30 seconds
# wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

try:
    # Check if the element is in an iframe (uncomment if needed)
    # iframe = driver.find_element(By.NAME, 'home-away')
    # driver.switch_to.frame(iframe)
    
    # Try to find the radio button
    radio_button = wait.until(EC.element_to_be_clickable((By.ID, "home-away2")))

    # Ensure it's checked and click it
    driver.execute_script("arguments[0].checked = true;", radio_button)
    radio_button.click()  # Trigger a click event

    # Wait for the table content to load after checking the radio button
    time.sleep(5)  # Give the page time to load

    # Scrape the table inside the div with id "league-chemp"
    table_div = wait.until(EC.presence_of_element_located((By.ID, "league-chemp")))

    # Parse the table with BeautifulSoup
    soup = BeautifulSoup(table_div.get_attribute('innerHTML'), 'html.parser')
    table = soup.find('table')

    # Extract table data
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        data.append(cols)

    # Print the scraped table data
    for row in data:
        print(row)

except Exception as e:
    # Take a screenshot for debugging purposes
    driver.save_screenshot("error_screenshot.png")
    print("Error:", e)
    print("Screenshot taken and saved as error_screenshot.png")

finally:
    # Close the WebDriver
    driver.quit()
