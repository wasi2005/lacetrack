from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Path to your chromedriver, adjust if needed
# service = Service('/path/to/chromedriver')
# driver = webdriver.Chrome(service=service)
driver = webdriver.Chrome()  # Assumes chromedriver is in PATH

driver.get('http://127.0.0.1:5000')
time.sleep(2)  # Wait for page to load
print('Page title:', driver.title)

driver.quit() 