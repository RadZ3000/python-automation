from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json

# Set up Firefox options for headless mode
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")

# Initialize the WebDriver with the specified options
print("Initializing...")
driver = webdriver.Firefox(options=firefox_options)
driver.implicitly_wait(0.5)


# Navigate to the initial page
print("Opening page...")
driver.get("https://www.txsmartbuy.com/contracts?filterBy=TXMAS")

# Find all elements with the link text "Details"
print("Finding 'Details' links...")
details_elements = driver.find_elements(By.LINK_TEXT, "Details")

# Create a list to store the hrefs
hrefs = []

# Iterate through the "Details" elements
for element in details_elements:
    # Get the href attribute and append it to the hrefs list
    hrefs.append(element.get_attribute("href"))

# Create a list to store the data
data_set = []


# Function to scrape data with retries
def scrape_data_with_retries(href):
    max_retries = 3
    retries = 0
    data_found = False

    while retries < max_retries and not data_found:
        try:
            # Explicitly wait for the "contractors" element to be present
            data = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "contractors"))
            )
            data_set.append(data.text)
            print("Data found and appended!")
            data_found = True
        except NoSuchElementException:
            # Handle the case when the "contractors" element is not found
            print("Data not found for this page. Retrying...")
            retries += 1

    if not data_found:
        data_set.append("Data not found for this page after retries")


# Loop through the hrefs and visit each URL
for href in hrefs:
    print(f"Visiting URL: {href}...")
    driver.get(href)
    scrape_data_with_retries(href)
    driver.back()

# Close the WebDriver when done
driver.quit()

# Organize and structure the data
structured_data = []

# Loop through the scraped data and split it into individual contract strings
for contract_string in data_set:
    # Split the contract string into lines
    lines = contract_string.split("\n")

    # Initialize a dictionary to store contract attributes
    contract_data = {}

    # Loop through the lines and extract attribute information
    for line in lines:
        key, value = line.split(": ", 1)
        contract_data[key] = value

    # Append the contract data dictionary to the structured_data list
    structured_data.append(contract_data)

# Save the structured data to a JSON file
with open("contract_data.json", "w", encoding="utf-8") as json_file:
    json.dump(structured_data, json_file, ensure_ascii=False, indent=4)

# Print the final result
print("Scraping complete. Data collected and saved to 'contract_data.json'.")
print(f"Total contracts scraped: {len(structured_data)}")
