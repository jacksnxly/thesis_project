import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import requests
from selenium.webdriver.common.action_chains import ActionChains
import traceback

def extract_html(url: str, output_path: str):
    # Set up Chrome options
    options = uc.ChromeOptions()
    
    # Two-phase mode: headless first, then normal
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    
    # Additional stealth options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--ignore-certificate-errors")
    
    # Enhanced fingerprint randomization
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]
    selected_ua = random.choice(user_agents)
    
    # Randomize browser fingerprint
    options.add_argument(f"user-agent={selected_ua}")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-3d-apis")
    options.add_argument("--disable-features=AudioServiceOutOfProcess")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-domain-reliability")
    options.add_argument("--disable-features=AudioServiceOutOfProcess")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-sync")
    options.add_argument("--force-color-profile=srgb")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--safebrowsing-disable-auto-update")
    options.add_argument("--password-store=basic")
    options.add_argument("--use-mock-keychain")
    
    print(f"Using User-Agent: {selected_ua}")
    
    # Proxy settings (optional)
    use_proxy = False  # Set to True and configure proxies if needed
    if use_proxy:
        proxies = [
            "http://proxy1:port",
            "http://proxy2:port",
            "http://proxy3:port"
        ]
        selected_proxy = random.choice(proxies)
        options.add_argument(f"--proxy-server={selected_proxy}")
        print(f"Using Proxy: {selected_proxy}")
    
    # Initialize WebDriver in headless mode first
    driver = uc.Chrome(
        options=options,
        version_main=None  # Automatically match Chrome version
    )
    
    # Get through initial Cloudflare check in headless mode
    driver.get(url)
    time.sleep(random.uniform(5, 10))
    
    # Restart browser in normal mode
    driver.quit()
    
    # Create new ChromeOptions for normal mode
    normal_options = uc.ChromeOptions()
    normal_options.add_argument("--start-maximized")
    normal_options.add_argument("--disable-blink-features=AutomationControlled")
    normal_options.add_argument("--disable-infobars")
    normal_options.add_argument("--disable-dev-shm-usage")
    normal_options.add_argument("--no-sandbox")
    normal_options.add_argument("--disable-gpu")
    normal_options.add_argument("--disable-extensions")
    normal_options.add_argument("--disable-popup-blocking")
    normal_options.add_argument("--disable-notifications")
    normal_options.add_argument("--disable-web-security")
    normal_options.add_argument("--disable-logging")
    normal_options.add_argument("--log-level=3")
    normal_options.add_argument("--ignore-certificate-errors")
    normal_options.add_argument(f"user-agent={selected_ua}")
    
    driver = uc.Chrome(
        options=normal_options,
        version_main=None  # Automatically match Chrome version
    )
    
    # Enhanced human-like behavior simulation
    print("Simulating human-like behavior...")
    time.sleep(random.uniform(3, 7))  # Initial delay
    
    # Enable network interception
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": selected_ua})
    
    # Random mouse movements with ActionChains
    actions = ActionChains(driver)
    try:
        # Move mouse in random patterns
        for _ in range(random.randint(5, 10)):
            x = random.randint(100, 1000)
            y = random.randint(100, 800)
            actions.move_by_offset(x, y).perform()
            time.sleep(random.uniform(0.2, 0.8))
            actions.move_by_offset(-x, -y).perform()
            time.sleep(random.uniform(0.2, 0.8))
            
        # Random scrolling with varying speeds
        for _ in range(random.randint(3, 6)):
            scroll_amount = random.randint(200, 800)
            scroll_speed = random.uniform(0.1, 0.5)
            driver.execute_script(f"""
                window.scrollBy({{
                    top: {scroll_amount},
                    left: 0,
                    behavior: 'smooth'
                }});
            """)
            time.sleep(scroll_speed)
    except Exception as e:
        print(f"Behavior simulation error: {str(e)}")
    
    try:
        # Navigate to Crunchbase login page
        login_url = "https://www.crunchbase.com/login"
        driver.get(login_url)
        
        # Wait for login form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[1]/div[1]/div/div[2]/input"))
        )
        
        # Fill in credentials using provided XPath
        print("Locating email field...")
        email_field = driver.find_element(By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[1]/div[1]/div/div[2]/input")
        print("Locating password field...")
        password_field = driver.find_element(By.XPATH, "/html/body/chrome/div/mat-sidenav-container/mat-sidenav-content/div/authentication-page/page-layout/div/div/div[2]/authentication/mat-card/mat-tab-group/div/mat-tab-body[1]/div/login/form/mat-form-field[2]/div[1]/div/div[2]/input")
        
        # Fill email field with retries
        print("Filling email field...")
        try:
            email_field.clear()
            time.sleep(0.5)
            for char in "jackson.ly@fs-students.de":
                email_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Human-like typing
            print("Email field filled successfully")
        except Exception as e:
            print(f"Error filling email field: {str(e)}")
            raise
        
        # Fill password field with retries
        print("Filling password field...")
        try:
            password_field.clear()
            time.sleep(0.5)
            for char in "Esslingerstr16!":
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Human-like typing
            print("Password field filled successfully")
        except Exception as e:
            print(f"Error filling password field: {str(e)}")
            raise
        
        # Wait for button to become enabled
        print("Waiting for login button to become enabled...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        WebDriverWait(driver, 10).until(
            lambda d: not login_button.get_attribute("disabled")
        )
        
        # Scroll button into view and click
        print("Clicking login button...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
        time.sleep(0.5)
        login_button.click()
        
        # Wait for login to complete or CAPTCHA to appear
        print("Waiting for login to complete...")
        try:
            # Wait for either successful login or CAPTCHA
            WebDriverWait(driver, 10).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "[data-test='user-menu']") or
                         d.find_elements(By.ID, "captcha-container")
            )
            
            # Check if CAPTCHA appeared
            if driver.find_elements(By.ID, "captcha-container"):
                print("CAPTCHA detected. Please complete the CAPTCHA in the browser window...")
                while driver.find_elements(By.ID, "captcha-container"):
                    time.sleep(1)
        except:
            print("Login process taking longer than expected...")
        
        # Navigate to target URL after login
        driver.get(url)
        print("Navigated to target URL after login")
        
        # Skip login verification since login is handled manually
        print("Assuming successful login, proceeding with HTML extraction...")
        
        # Wait for page to fully load
        time.sleep(5)  # Additional wait for dynamic content
        
        # Extract HTML
        html_content = driver.page_source
        
        # Save HTML to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML successfully saved to {output_path}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
    finally:
        # Clean up
        driver.quit()

if __name__ == "__main__":
    target_url = "https://www.crunchbase.com/discover/organization.companies/b14ee2c80c30667be900f0b2b02d34fc"
    output_file = "test/web_extracts/crunchbase_extract.html"
    extract_html(target_url, output_file)
