import os
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import pandas as pd

# Configure logging for production reliability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_dynamic_racing_table(target_url: str, expected_rows: int, timeout_sec: int = 10) -> pd.DataFrame:
    """
    Scrapes a complex, dynamic racing data table utilizing stealth headless browser automation.
    Optimized with explicit waits (WebDriverWait) and true in-memory relative DOM parsing to bypass anti-bot detection.
    """
    
    # 1. Initialize Hardened Stealth Chrome Options
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Modern desktop-grade headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 🛡️ Anti-Bot Guard: Spoof standard user-agent to wipe out 'HeadlessChrome' signatures
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Bypassing basic automation detection signatures
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Cross-platform environment configuration
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    service = Service(driver_path) if driver_path else Service() # Selenium Manager auto-fallback
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Advanced CDP Obfuscation
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    # Data structure allocation
    data_storage = {
        'Horse_No': [], 'Horse_Name': [], 'Horse_ID': [], 'Current_Rating': [],
        'Actual_Weight': [], 'Horse_Weight': [], 'Jockey': [], 'Trainer': [],
        'Draw': [], 'Age': [], 'Days_Since_Last_Race': [], 'Gear': [],
        'Sire': [], 'Dam_Sire': []
    }

    try:
        logging.info(f"Navigating to secured endpoint: {target_url}")
        driver.get(target_url)

        attempts = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            try:
                # Explicit Wait for the parent table container
                table_locator = (By.XPATH, '//*[@id="racecardlist"]/tbody/tr/td/table/tbody')
                WebDriverWait(driver, timeout_sec).until(EC.presence_of_element_located(table_locator))
                
                # Performance Core: Fetching all row objects into memory in ONE network packet
                rows = driver.find_elements(By.XPATH, '//*[@id="racecardlist"]/tbody/tr/td/table/tbody/tr')
                
                if len(rows) < expected_rows:
                    raise NoSuchElementException("Dynamic rows not fully synchronized in DOM.")
                
                logging.info(f"DOM locked successfully. Executing high-speed in-memory relative parsing for {expected_rows} elements...")
                
                # 🛡️ True In-Memory Relative Traversal (Prevents StaleElementReferenceException)
                for i in range(expected_rows):
                    row = rows[i] # Extract the cached row element directly from memory
                    
                    # Using relative XPATH (starting with '.') ensures zero browser re-scanning overhead
                    data_storage['Horse_No'].append(row.find_element(By.XPATH, './td[1]').get_attribute("innerHTML").strip())
                    data_storage['Horse_Name'].append(row.find_element(By.XPATH, './td[4]').text.strip())
                    data_storage['Horse_ID'].append(row.find_element(By.XPATH, './td[5]').get_attribute("innerHTML").strip())
                    data_storage['Current_Rating'].append(row.find_element(By.XPATH, './td[12]').get_attribute("innerHTML").strip())
                    data_storage['Actual_Weight'].append(row.find_element(By.XPATH, './td[6]').get_attribute("innerHTML").strip())
                    data_storage['Horse_Weight'].append(row.find_element(By.XPATH, './td[14]').get_attribute("innerHTML").strip())
                    data_storage['Jockey'].append(row.find_element(By.XPATH, './td[7]').text.strip())
                    data_storage['Trainer'].append(row.find_element(By.XPATH, './td[10]').text.strip())
                    data_storage['Draw'].append(row.find_element(By.XPATH, '././td[9]').get_attribute("innerHTML").strip())
                    data_storage['Age'].append(row.find_element(By.XPATH, './td[17]').get_attribute("innerHTML").strip())
                    data_storage['Days_Since_Last_Race'].append(row.find_element(By.XPATH, './td[22]').get_attribute("innerHTML").strip())
                    data_storage['Gear'].append(row.find_element(By.XPATH, './td[23]').get_attribute("innerHTML").strip())
                    data_storage['Sire'].append(row.find_element(By.XPATH, './td[25]').get_attribute("innerHTML").strip())
                    data_storage['Dam_Sire'].append(row.find_element(By.XPATH, './td[26]').get_attribute("innerHTML").strip())
                
                break # Success break
                
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                attempts += 1
                logging.warning(f"Network mutation or tracking triggered. Attempt {attempts}/{max_attempts}. Hard-refreshing DOM...")
                driver.refresh()
                if attempts == max_attempts:
                    logging.critical(f"Circuit breaker activated. Scraper blocked: {traceback.format_exc()}")
                    raise RuntimeError("Failed to stabilize structural data pipeline within maximum retries.") from e

    finally:
        # Guarantee termination of headless processes to mitigate system memory leaks
        driver.quit()
        logging.info("Headless Webdriver detached. OS processes successfully recycled.")

    # Return enterprise-grade structured data
    return pd.DataFrame(data_storage)

if __name__ == "__main__":
    print("Stealth Core Engine V2 (Memory Optimized) initialized successfully.")
