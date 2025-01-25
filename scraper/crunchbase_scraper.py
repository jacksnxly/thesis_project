import csv
import os
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
import traceback

class CrunchbaseScraper:
    def __init__(self):
        self.driver = None
        self.csv_columns = [
            "Organization Name",
            "Founded Date",
            "Headquarters Location",
            "Industries",
            "Number of Employees",
            "Number of Funding Rounds",
            "Total Funding Amount",
            "Last Funding Type",
            "Last Funding Date",
            "Last Funding Amount",
            "Number of Investors",
            "Number of Articles",
            "Description"
        ]
        self.data: List[Dict] = []

    def initialize_browser(self):
        """Initialize browser with authentication"""
        # Set up Chrome options
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Randomize user agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        selected_ua = random.choice(user_agents)
        options.add_argument(f"user-agent={selected_ua}")
        
        # Initialize WebDriver
        self.driver = uc.Chrome(options=options, version_main=None)
        
        # Navigate to Crunchbase login
        login_url = "https://www.crunchbase.com/login"
        print(f"Navigating to login page: {login_url}")
        self.driver.get(login_url)
        
        # Wait for login form and fill credentials
        try:
            # Wait for login form to load
            print("Waiting for login form...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[1]/div[1]/div/div[2]/input"))
            )
            
            # Fill in credentials using XPath
            print("Filling email field...")
            for attempt in range(3):  # Retry up to 3 times
                try:
                    # Re-locate email field before each interaction
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[1]/div[1]/div/div[2]/input"))
                    )
                    email_field.clear()
                    time.sleep(0.5)
                    for char in "jackson.ly@fs-students.de":
                        # Re-locate field before each character
                        email_field = self.driver.find_element(By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[1]/div[1]/div/div[2]/input")
                        email_field.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    print("Email field filled successfully")
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == 2:  # Last attempt
                        raise
                    time.sleep(1)  # Wait before retrying
            
            print("Filling password field...")
            for attempt in range(3):  # Retry up to 3 times
                try:
                    # Re-locate password field before each interaction
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[2]/div[1]/div/div[2]/input"))
                    )
                    password_field.clear()
                    time.sleep(0.5)
                    for char in "Esslingerstr16!":
                        # Re-locate field before each character
                        password_field = self.driver.find_element(By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[2]/div[1]/div/div[2]/input")
                        password_field.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                    print("Password field filled successfully")
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == 2:  # Last attempt
                        raise
                    time.sleep(1)  # Wait before retrying
            
            print("Waiting for login button to become enabled...")
            for attempt in range(3):  # Retry up to 3 times
                try:
                    # Re-locate login button before each interaction
                    login_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                    )
                    
                    # Check if button is enabled
                    WebDriverWait(self.driver, 10).until(
                        lambda d: not d.find_element(By.CSS_SELECTOR, "button[type='submit']").get_attribute("disabled")
                    )
                    
                    print("Clicking login button...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
                    time.sleep(0.5)
                    
                    # Re-locate button before clicking
                    login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    login_button.click()
                    break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == 2:  # Last attempt
                        raise
                    time.sleep(1)  # Wait before retrying
            
            print("Waiting for login to complete...")
            try:
                # Wait for either successful login or CAPTCHA
                WebDriverWait(self.driver, 20).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "[data-test='user-menu']") or
                            d.find_elements(By.ID, "captcha-container")
                )
                
                # Check if CAPTCHA appeared
                if self.driver.find_elements(By.ID, "captcha-container"):
                    print("CAPTCHA detected. Please complete the CAPTCHA in the browser window...")
                    while self.driver.find_elements(By.ID, "captcha-container"):
                        time.sleep(1)
            except:
                print("Login process taking longer than expected...")
            
            # Navigate to target URL after login
            target_url = "https://www.crunchbase.com/discover/organization.companies/04dd8d7c28b9e75b12cd06e65185ceea"
            print(f"Navigating to target URL: {target_url}")
            self.driver.get(target_url)
            
            # Wait for page load
            print("Waiting for page to load...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "grid-body .body-wrapper"))
            )
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            traceback.print_exc()
            # Take screenshot for debugging
            self.driver.save_screenshot("login_error.png")
            print("Screenshot saved as login_error.png")

    def wait_for_table(self):
        """Wait for the grid to load"""
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "grid-body .body-wrapper"))
        )

    def extract_table_data(self):
        """Extract data from current page's grid"""
        expected_rows = 50
        rows = []
        attempts = 0
        max_attempts = 5
        
        while len(rows) < expected_rows and attempts < max_attempts:
            # Scroll through table in smaller increments
            table = self.driver.find_element(By.CSS_SELECTOR, "grid-body")
            row_height = 50  # Approximate row height in pixels
            scroll_increment = 500  # Scroll 500px at a time
            
            # Scroll from top to bottom in increments
            current_scroll = 0
            while current_scroll < table.size['height']:
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[1];", 
                    table, current_scroll
                )
                current_scroll += scroll_increment
                time.sleep(0.5)  # Wait for rows to load
                
                # Get current visible rows
                rows = self.driver.find_elements(By.CSS_SELECTOR, "grid-row")
                if len(rows) >= expected_rows:
                    break
            
            # Verify row count
            if len(rows) < expected_rows:
                print(f"Found only {len(rows)} rows, retrying... (attempt {attempts + 1}/{max_attempts})")
                attempts += 1
                time.sleep(2)
        
        if len(rows) < expected_rows:
            print(f"Warning: Only found {len(rows)} rows out of expected {expected_rows}")
        
        print(f"Found {len(rows)} rows on current page")
        
        for row in rows:
            try:
                row_data = {
                    "Organization Name": self._get_grid_cell_text(row, "identifier"),
                    "Founded Date": self._get_grid_cell_text(row, "founded_on"),
                    "Headquarters Location": self._get_grid_cell_text(row, "location_identifiers"),
                    "Industries": self._get_grid_cell_text(row, "categories"),
                    "Number of Employees": self._get_grid_cell_text(row, "num_employees_enum"),
                    "Number of Funding Rounds": self._get_grid_cell_text(row, "num_funding_rounds"),
                    "Total Funding Amount": self._get_grid_cell_text(row, "funding_total"),
                    "Last Funding Type": self._get_grid_cell_text(row, "last_funding_type"),
                    "Last Funding Date": self._get_grid_cell_text(row, "last_funding_at"),
                    "Last Funding Amount": self._get_grid_cell_text(row, "last_funding_total"),
                    "Number of Investors": self._get_grid_cell_text(row, "num_investors"),
                    "Number of Articles": self._get_grid_cell_text(row, "num_articles"),
                    "Description": self._get_grid_cell_text(row, "short_description")
                }
                self.data.append(row_data)
            except Exception as e:
                print(f"Error extracting row: {e}")
                continue

    def _get_grid_cell_text(self, row, column_id: str) -> str:
        """Helper to get text from a grid cell"""
        try:
            if column_id == "num_articles":
                # Try multiple selector patterns for Number of Articles
                try:
                    # First try: Specific XPath
                    element = row.find_element(By.XPATH, ".//grid-cell[contains(@data-columnid, 'num_articles')]//a")
                    return element.text.strip() if element.text else "0"
                except:
                    try:
                        # Second try: CSS selector
                        element = row.find_element(By.CSS_SELECTOR, "grid-cell[data-columnid='num_articles'] a")
                        return element.text.strip() if element.text else "0"
                    except:
                        try:
                            # Third try: Text content fallback
                            element = row.find_element(By.CSS_SELECTOR, "grid-cell[data-columnid='num_articles']")
                            return element.text.strip() if element.text else "0"
                        except:
                            return "0"
            else:
                element = row.find_element(By.CSS_SELECTOR, f"grid-cell[data-columnid='{column_id}']")
            return element.text.strip() if element.text else "N/A"
        except:
            return "N/A"

    def handle_pagination(self):
        """Handle pagination through all pages"""
        page_count = 1
        max_retries = 3
        
        while True:
            # Extract current page data
            print(f"Scraping page {page_count}...")
            self.extract_table_data()
            
            # Check for next page
            retries = 0
            while retries < max_retries:
                try:
                    # Try multiple possible selectors for pagination controls
                    print("Looking for pagination controls...")
                    next_button = None
                    
                    # Try multiple selector patterns with increased timeout
                    next_button = None
                    selector_patterns = [
                        ("CSS", "div.pagination-controls a.next-page-button"),
                        ("CSS", "a[aria-label='Next page']"),
                        ("CSS", "button.next-page"),
                        ("CSS", "a.next"),
                        ("XPATH", "//a[contains(text(), 'Next')]"),
                        ("XPATH", "//button[contains(text(), 'Next')]"),
                        ("CSS", "button[data-test='pagination-next-button']"),
                        ("CSS", "a.pagination-next"),
                        ("CSS", "li.next a"),
                        ("CSS", "a.pagination__next"),
                        ("XPATH", "//*[contains(@class, 'next')]"),
                        ("XPATH", "//*[contains(@class, 'pagination-next')]"),
                        ("CSS", "button[aria-label='Next']"),
                        ("CSS", "a[title='Next']")
                    ]
                    
                    # Add scroll and wait before looking for pagination controls
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    for selector_type, selector in selector_patterns:
                        try:
                            if selector_type == "XPATH":
                                next_button = WebDriverWait(self.driver, 2).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                            else:
                                next_button = WebDriverWait(self.driver, 2).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                )
                            break
                        except:
                            continue
                    
                    if not next_button:
                        # Double check by scrolling and waiting
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        # Try finding next button again
                        for selector_type, selector in selector_patterns:
                            try:
                                if selector_type == "XPATH":
                                    next_button = self.driver.find_element(By.XPATH, selector)
                                else:
                                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                break
                            except:
                                continue
                        
                        if not next_button:
                            print("No next page button found - likely reached last page")
                            return
                    
                    print(f"Next button found: {next_button}")
                    
                    # Additional check for disabled state
                    if not next_button.is_displayed() or not next_button.is_enabled():
                        print("Next button is not active")
                        return
                    
                    # Enhanced last page detection
                    is_disabled = next_button.get_attribute("disabled") or \
                                "disabled" in next_button.get_attribute("class") or \
                                not next_button.is_enabled() or \
                                not next_button.is_displayed()
                    
                    if is_disabled:
                        print("Reached last page (next button disabled)")
                        return
                    
                    # Additional check for last page by comparing row counts
                    current_rows = len(self.driver.find_elements(By.CSS_SELECTOR, "grid-row"))
                    next_button.click()
                    time.sleep(2)  # Wait for potential page load
                    next_page_rows = len(self.driver.find_elements(By.CSS_SELECTOR, "grid-row"))
                    
                    if next_page_rows <= current_rows:
                        print("Reached last page (no new rows loaded)")
                        self.driver.back()  # Return to previous page
                        time.sleep(2)
                        return
                    
                    # Scroll next button into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(0.5)
                    next_button.click()
                    
                    # Wait for next page to load
                    self.wait_for_table()
                    page_count += 1
                    
                    # Add delay to avoid rate limiting
                    time.sleep(random.uniform(1, 2))
                    break
                    
                except Exception as e:
                    print(f"Pagination error (attempt {retries + 1}): {e}")
                    retries += 1
                    if retries < max_retries:
                        # Try refreshing the page
                        print("Refreshing page and retrying...")
                        self.driver.refresh()
                        self.wait_for_table()
                        time.sleep(2)
                    else:
                        print("Max retries reached. Ending pagination.")
                        traceback.print_exc()
                        return

    def save_to_csv(self):
        """Save collected data to CSV"""
        output_file = "data/crunchbase_data.csv"
        try:
            # Check if file exists to determine if we need to write header
            file_exists = os.path.exists(output_file)
            
            with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.csv_columns, 
                                     delimiter=',', quotechar='"', 
                                     quoting=csv.QUOTE_MINIMAL)
                
                # Only write header if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                
                # Clean and write data
                cleaned_data = []
                for row in self.data:
                    cleaned_row = {}
                    for key, value in row.items():
                        # Remove any special characters that might break CSV format
                        if isinstance(value, str):
                            value = value.replace('\n', ' ').replace('\r', '')
                            value = value.replace('"', "'")  # Replace double quotes with single
                        cleaned_row[key] = value
                    cleaned_data.append(cleaned_row)
                
                writer.writerows(cleaned_data)
                print(f"Appended {len(cleaned_data)} rows to {output_file}")
                
                # Clear data for next page
                self.data = []
        except Exception as e:
            print(f"Error saving CSV: {e}")

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    scraper = CrunchbaseScraper()
    try:
        scraper.initialize_browser()
        scraper.wait_for_table()
        scraper.handle_pagination()
        scraper.save_to_csv()
    except Exception as e:
        print(f"Scraping error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
