from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Store XPath and CSS selectors in variables for easy modification
XPATH_CLOSE_BANNER_BUTTON = "//*[@id='data-protection-agree']"  # Updated XPath for the close button
XPATH_2D_STRUCTURE_TAB = "/html/body/div[1]/div/div/div/div/div[4]/div/ul/li[3]/a/uib-tab-heading"
CSS_SELECTOR_STRUCTURE = "span.notation-font"
BANNER_ID = "data-protection-banner"

# Function to fetch secondary structure
def fetch_secondary_structure(url):
    try:
        # Initialize WebDriver (ensure chromedriver is in PATH or specify path)
        driver = webdriver.Chrome()  # Ensure chromedriver is in PATH or specify path
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for body tag to load

        # Attempt to close the data protection banner
        try:
            # Wait for the close button to be clickable
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_CLOSE_BANNER_BUTTON)))
            close_button = driver.find_element(By.XPATH, XPATH_CLOSE_BANNER_BUTTON)

            # Click the button to dismiss the banner using JavaScript to force the click
            driver.execute_script("arguments[0].click();", close_button)

            # Wait for the banner to disappear
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.ID, BANNER_ID)))
            print("Banner dismissed successfully.")
        except Exception as e:
            print(f"Error dismissing banner: {e}")

        # Use WebDriverWait to ensure the "2D Structure" tab is clickable by full XPath
        structure_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_2D_STRUCTURE_TAB))
        )

        # Click the "2D Structure" tab directly (no scrolling needed)
        structure_button.click()

        # Wait for the structure to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CSS_SELECTOR_STRUCTURE))
        )

        # Find the span containing the dot-bracket notation
        structure_element = driver.find_element(By.CSS_SELECTOR, CSS_SELECTOR_STRUCTURE)
        structure_text = structure_element.text.strip() if structure_element else None

        # Close the browser
        driver.quit()

        return structure_text
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


unf_file_path = 'data/homo_sapiens_rrna_data.csv'
output_format_path = 'data/homo_structures.csv'
scrape_structures(unf_file_path, output_format_path)
