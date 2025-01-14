import time
import pyperclip
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Store XPath and CSS selectors in variables for easy modification
XPATH_CLOSE_BANNER_BUTTON = "//*[@id='data-protection-agree']"
XPATH_2D_STRUCTURE_TAB = "/html/body/div[1]/div/div/div/div/div[4]/div/ul/li[3]/a/uib-tab-heading"
XPATH_COPY_DOT_BRACKET_BUTTON = "/html/body/div[1]/div/div/div/div/div[4]/div/div/div[3]/r2dt-web//html/body/div[2]/div[1]/div/div[2]/button[3]"
BANNER_ID = "data-protection-banner"

# Function to fetch secondary structure
def fetch_secondary_structure(url):
    try:
        # Initialize WebDriver with options to bypass SSL/TLS errors
        service = Service("C:/Users/bsand/Documents/WebDrivers/chromedriver-win64/chromedriver.exe")  # Provide path to chromedriver.exe
        options = Options()
        options.add_argument('--ignore-certificate-errors')  # Ignore SSL certificate errors
        options.add_argument('--disable-web-security')  # Disable web security features
        driver = webdriver.Chrome(service=service, options=options)

        # Wait for the page to load
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for body tag to load

        # Attempt to close the data protection banner
        try:
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, XPATH_CLOSE_BANNER_BUTTON)))
            close_button = driver.find_element(By.XPATH, XPATH_CLOSE_BANNER_BUTTON)
            driver.execute_script("arguments[0].click();", close_button)
            WebDriverWait(driver, 15).until(EC.invisibility_of_element_located((By.ID, BANNER_ID)))
            print("Banner dismissed successfully.")
        except Exception as e:
            print(f"Error dismissing banner: {e}")

        # Wait for the "2D Structure" tab to be clickable
        structure_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_2D_STRUCTURE_TAB))
        )

        # Click the "2D Structure" tab
        driver.execute_script("arguments[0].click();", structure_button)

        # Wait for the "Copy Dot-Bracket Notation" button to become clickable
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_COPY_DOT_BRACKET_BUTTON))
        )

        # Click the "Copy Dot-Bracket Notation" button
        copy_button = driver.find_element(By.XPATH, XPATH_COPY_DOT_BRACKET_BUTTON)
        driver.execute_script("arguments[0].click();", copy_button)

        # Wait a bit for the content to be copied to the clipboard
        time.sleep(1)

        # Use pyperclip to get the content from the clipboard
        dot_bracket_notation = pyperclip.paste()

        # Print the dot-bracket notation for debugging purposes
        print(dot_bracket_notation)

        # Close the browser
        driver.quit()

        return dot_bracket_notation
    except Exception as e:
        print(f"Error fetching secondary structure from {url}: {e}")
        driver.quit()
        return None


# Main function to process the CSV and scrape secondary structures
def scrape_structures(csv_path, output_csv):
    # Read the CSV with the URLs
    df = pd.read_csv(csv_path)

    # Create a new column 'Structure' to store the secondary structure
    df['Structure'] = df['URL'].apply(fetch_secondary_structure)

    # Save the updated DataFrame to a new CSV
    df.to_csv(output_csv, index=False)
    print(f"Scraping completed. Data saved to {output_csv}")


unf_file_path = 'data/homo_sapiens_rrna_data.csv'  # Path to your input CSV file
output_format_path = 'data/homo_structures.csv'  # Path to the output CSV
scrape_structures(unf_file_path, output_format_path)
