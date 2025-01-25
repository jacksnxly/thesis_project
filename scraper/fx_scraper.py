import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_yahoo_fx():
    # Configure browser with user agent and visible mode
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Initialize driver with WebDriver Manager
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # Load Yahoo Finance EUR/USD historical data
        driver.get("https://finance.yahoo.com/quote/EURUSD=X/history/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAA9TJvWDPvzZXGemg_gbAvzluEMtnZ5wzKFys67Y2tDataSKdfz_d3Fyh8CfvAC6seadiI1NIFPra-cTGaaSwkKRqsh0vvRbTknMx5PX4WlX7MLcV0b224cGv2fNzQOLYBR3DkMJRT7YPvQNGprzI4xsnKCsk3HORObgkd1V1CgD&period1=1577836800&period2=1616284800")
        
        # Wait for initial table load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )

        # Scroll to bottom in increments
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow time for loading
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Parse page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        
        # Extract headers and rows
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip header row
            cols = [td.get_text(strip=True) for td in tr.find_all('td')]
            if len(cols) == len(headers):  # Filter out empty rows
                rows.append(cols)

        # Reverse rows to get chronological order (oldest first)
        rows.reverse()

        # Write to CSV
        with open('data/raw/fx_data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([headers[0], headers[4]])  # Date and Close columns
            for row in rows:
                writer.writerow([row[0], row[4]])

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_yahoo_fx()
