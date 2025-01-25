import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import requests
import json
import config
import random
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

class SocialScraper:
    def __init__(self, input_csv):
        self.input_csv = input_csv
        self.driver = None
        self.df = None
        self.deepseek_api_key = config.DEEPSEEK_API_KEY
        
    def preprocess_csv(self):
        """Read and preprocess the input CSV file"""
        try:
            # Read CSV
            self.df = pd.read_csv(self.input_csv)
            
            # Verify required columns exist
            if not {'Organization Name', 'Industries'}.issubset(self.df.columns):
                raise ValueError("CSV must contain 'Organization Name' and 'Industries' columns")
                
            # Clean Industry field - take first industry before comma
            self.df['Cleaned Industry'] = self.df['Industries'].apply(
                lambda x: x.split(',')[0].split(':')[0].strip() if isinstance(x, str) and x else None
            )
            
            # Create search queries
            self.df['Search Query'] = self.df.apply(
                lambda row: f"{row['Organization Name']} {row['Cleaned Industry']} startup website", 
                axis=1
            )
            
            # Initialize result columns
            self.df['LinkedIn Followers'] = None
            self.df['Twitter Followers'] = None
            self.df['Instagram Followers'] = None
            
            return True
            
        except Exception as e:
            print(f"Error preprocessing CSV: {str(e)}")
            return False
            
    def setup_browser(self):
        """Initialize Selenium WebDriver"""
        try:
            # Clean up any existing driver instances
            if hasattr(self, 'driver') and self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-dev-tools')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Try to initialize WebDriver with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    self.driver.implicitly_wait(5)  # Reduced from 15 to 5 seconds
                    self.driver.set_page_load_timeout(15)  # Reduced from 30 to 15 seconds
                    return True
                except Exception as e:
                    print(f"WebDriver initialization attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                        continue
                    raise
                    
        except Exception as e:
            print(f"Error setting up browser: {str(e)}")
            print("Make sure chromedriver is installed and matches your Chrome version")
            print("You can download it from: https://chromedriver.chromium.org/downloads")
            return False
            
    def login_linkedin(self):
        """Automatically login to LinkedIn"""
        try:
            self.driver.get('https://www.linkedin.com/login')
            
            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            
            # Fill in credentials
            email_field = self.driver.find_element(By.ID, 'username')
            email_field.send_keys(os.getenv('LINKEDIN_EMAIL'))
            
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.send_keys(os.getenv('LINKEDIN_PASSWORD'))
            password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-global-typeahead__input'))
            )
            return True
            
        except Exception as e:
            print(f"Error logging into LinkedIn: {str(e)}")
            return False
            
    def login_twitter(self):
        """Automatically login to Twitter/X"""
        try:
            # Try to load existing session first
            self.driver.get('https://x.com/login')
            
            # Check if already logged in
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/compose/tweet"]'))
                )
                return True
            except:
                # If not logged in, perform login
                self.driver.get('https://twitter.com/i/flow/login')
                
                # Wait for username field
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'text'))
                )
                
                # Enter username
                username_field = self.driver.find_element(By.NAME, 'text')
                username_field.send_keys(os.getenv('TWITTER_USERNAME'))
                username_field.send_keys(Keys.RETURN)
                
                # Wait for password field
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'password'))
                )
                
                # Enter password
                password_field = self.driver.find_element(By.NAME, 'password')
                password_field.send_keys(os.getenv('TWITTER_PASSWORD'))
                password_field.send_keys(Keys.RETURN)
                
                # Wait for login to complete
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="/compose/tweet"]'))
                )
                return True
            
        except Exception as e:
            print(f"Error logging into Twitter/X: {str(e)}")
            return False
        
    def google_search(self, query):
        """Perform Google search and extract result URLs"""
        try:
            self.driver.get('https://www.google.com')
            
            # Handle cookie banner if present
            try:
                reject_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.ID, 'W0wltc'))
                )
                reject_button.click()
            except:
                pass
                
            search_box = self.driver.find_element(By.NAME, 'q')
            search_box.send_keys(query)
            search_box.submit()
            
            # Handle captcha if needed
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, 'captcha-form'))
                )
                print("Captcha detected. Please solve it in the browser...")
                input("Press Enter when captcha is solved...")
            except:
                pass
                
            # Wait for results to load
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h3'))
            )
            
            # Extract URLs from search results (limit to first 5)
            results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g a')
            urls = [result.get_attribute('href') for result in results if result.get_attribute('href')]
            return urls[:5]  # Only return first 5 URLs
            
        except Exception as e:
            print(f"Error during Google search: {str(e)}")
            return []
            
    def get_company_website(self, company_name, industry, urls):
        """Use DeepSeek API to select most likely company website"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.deepseek_api_key}'
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Given these URLs: {urls}\n\nFor company: {company_name} in industry: {industry}\n\nWhich is most likely the official website? Return only the URL."
                    }
                ]
            }
            
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that identifies official company websites."
                        },
                        {
                            "role": "user",
                            "content": f"Given these top 5 URLs from search results: {urls}\n\nFor company: {company_name} in industry: {industry}\n\nWhich is most likely the official website? Return only the URL."
                        }
                    ],
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(result['choices'][0]['message']['content'])
                return result['choices'][0]['message']['content']
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling DeepSeek API: {str(e)}")
            return None
            
    def extract_social_links(self, url):
        """Extract social media links from company website"""
        try:
            self.driver.get(url)
            social_links = {}
            
            # Search entire page for social media links
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            # Common social media patterns to look for
            social_patterns = {
                'linkedin': ['linkedin.com', 'linked.in'],
                'twitter': ['twitter.com', 'x.com', 'twitter.com/'],
                'instagram': ['instagram.com', 'instagr.am']
            }
            
            # Check all links on page
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        # Check for social media patterns
                        for platform, patterns in social_patterns.items():
                            if any(pattern in href.lower() for pattern in patterns):
                                if platform not in social_links:
                                    social_links[platform] = href
                                    
                        # Check for social media icons
                        icon_classes = link.get_attribute('class') or ''
                        if any(x in icon_classes.lower() for x in ['social', 'icon']):
                            if 'linkedin' in icon_classes.lower() and 'linkedin' not in social_links:
                                social_links['linkedin'] = href
                            elif 'twitter' in icon_classes.lower() and 'twitter' not in social_links:
                                social_links['twitter'] = href
                            elif 'instagram' in icon_classes.lower() and 'instagram' not in social_links:
                                social_links['instagram'] = href
                except Exception as e:
                    print(f"Error processing link: {str(e)}")
                    continue
                                
            # If no links found, try searching page text
            if not social_links:
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
                social_text_patterns = {
                    'linkedin': ['linkedin.com/', 'linked.in/'],
                    'twitter': ['twitter.com/', 'x.com/'],
                    'instagram': ['instagram.com/', 'instagr.am/']
                }
                
                for platform, patterns in social_text_patterns.items():
                    for pattern in patterns:
                        if pattern in page_text:
                            # Try to extract the full URL from text
                            start = page_text.find(pattern)
                            end = page_text.find(' ', start)
                            if end == -1:
                                end = len(page_text)
                            potential_url = page_text[start:end].strip()
                            if 'http' not in potential_url:
                                potential_url = 'https://' + potential_url
                            social_links[platform] = potential_url
                            break
                                
            return social_links
            
        except Exception as e:
            print(f"Error extracting social links: {str(e)}")
            return {}
            
    def scrape_followers(self, platform, url):
        """Scrape follower count from social media platform"""
        try:
            # Open new tab and switch to it
            self.driver.execute_script(f"window.open('{url}')")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Platform-specific scraping logic
            if platform == 'linkedin':
                # Wait for LinkedIn page to load with multiple selectors
                selectors = [
                    'div.org-top-card',  # Main company card
                    'div.org-top-card-summary-info-list__info-item',  # New layout
                    'div.org-top-card-summary__follower-count',  # Old layout
                    'div.org-top-card-primary-content'  # Alternative
                ]
                
                element_found = None
                for selector in selectors:
                    try:
                        element_found = WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if element_found:
                            print(f"LinkedIn page loaded successfully using selector: {selector}")
                            break
                    except:
                        continue
                
                if not element_found:
                    print("Failed to load LinkedIn page - no matching elements found")
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return None
                
                # Scroll to ensure all elements are loaded
                self.driver.execute_script("window.scrollBy(0, 500)")
                time.sleep(1)
                
                # Try to find the full info list container
                info_list = None
                info_list_selectors = [
                    'div.org-top-card-summary-info-list',  # New layout
                    'div.org-top-card-summary__follower-count',  # Old layout
                    'div.org-top-card-primary-content'  # Alternative
                ]
                
                for selector in info_list_selectors:
                    try:
                        info_list = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if info_list:
                            print(f"Found info list container using selector: {selector}")
                            break
                    except:
                        continue
                
                if not info_list:
                    print("Could not locate info list container")
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return None
                
                # Get the HTML of the entire info list
                html_content = info_list.get_attribute('outerHTML')
                
                # Format HTML to be more concise
                soup = BeautifulSoup(html_content, 'html.parser')
                formatted_html = soup.prettify()
                
                # Save HTML to file for AI analysis
                os.makedirs('debug/linkedin', exist_ok=True)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"debug/linkedin/{timestamp}_{url.split('/')[-1]}.html"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(formatted_html)
                
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return filename
                
            elif platform == 'twitter':
                xpath = "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span"
            elif platform == 'instagram':
                xpath = "//header//ul//li[2]//span"
                
            # Wait for element with retries
            for attempt in range(5):
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    followers = element.text
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return followers
                except:
                    if attempt < 4:
                        self.driver.refresh()
                        time.sleep(2)
                        
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return None
            
        except Exception as e:
            print(f"Error scraping {platform} followers: {str(e)}")
            return None
            
    def save_results(self, output_csv):
        """Save results to output CSV"""
        try:
            self.df.to_csv(output_csv, index=False)
            return True
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            return False
            
    def extract_followers_from_html(self, html_content):
        """Use AI to extract follower count from LinkedIn HTML"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.deepseek_api_key}'
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that extracts follower counts from LinkedIn company page HTML. 
                        The follower count may be formatted with abbreviations like 'k' for thousand or 'm' for million.
                        Always return the follower count as a pure numeric value without any formatting.
                        Examples:
                        - '1k' → 1000
                        - '2.5k' → 2500
                        - '1m' → 1000000
                        - '1.2m' → 1200000
                        If no follower count is found, return 0."""
                    },
                    {
                        "role": "user",
                        "content": f"Given this LinkedIn company page HTML: {html_content}\n\nExtract the follower count number. Convert any formatted numbers to pure numeric values. Return only the number."
                    }
                ]
            }
            
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                followers = result['choices'][0]['message']['content']
                print(f"Raw AI response: {followers}")
                if followers.isdigit():
                    print(f"Successfully parsed followers: {followers}")
                    return int(followers)
                else:
                    print(f"AI returned non-numeric value: {followers}")
            else:
                print(f"API error: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"Error extracting followers from HTML: {str(e)}")
            return None

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    scraper = SocialScraper('data/raw/part15.csv')
    
    if scraper.preprocess_csv():
        if scraper.setup_browser():
            # Login to LinkedIn in first tab
            if not scraper.login_linkedin():
                print("Failed to login to LinkedIn - some features may not work")
                
            # Open new tab for Twitter/X login
            scraper.driver.execute_script("window.open('about:blank')")
            scraper.driver.switch_to.window(scraper.driver.window_handles[1])
            
            if not scraper.login_twitter():
                print("Failed to login to Twitter/X - some features may not work")
                
            # Switch back to first tab for processing
            scraper.driver.switch_to.window(scraper.driver.window_handles[0])
            
            # Process each company
            for index, row in scraper.df.iterrows():
                print(f"\nProcessing {row['Organization Name']}...")
                
                # Google search and website selection
                urls = scraper.google_search(row['Search Query'])
                if urls:
                    website = scraper.get_company_website(
                        row['Organization Name'],
                        row['Cleaned Industry'],
                        urls
                    )
                    
                    if website:
                        # Extract social links
                        social_links = scraper.extract_social_links(website)
                        
                        # Scrape followers for each platform
                        for platform, url in social_links.items():
                            result = scraper.scrape_followers(platform, url)
                            if result:
                                if platform == 'linkedin':
                                    # Process LinkedIn HTML file with AI
                                    with open(result, 'r', encoding='utf-8') as f:
                                        html_content = f.read()
                                    
                                    followers = scraper.extract_followers_from_html(html_content)
                                    if followers:
                                        print(f"Extracted {followers} followers for {row['Organization Name']}")
                                        scraper.df.at[index, f'{platform.capitalize()} Followers'] = followers
                                    else:
                                        print(f"Failed to extract followers from HTML for {row['Organization Name']}")
                                else:
                                    scraper.df.at[index, f'{platform.capitalize()} Followers'] = result
                                
            # Save results
            output_file = scraper.input_csv.replace('part', '')
            if scraper.save_results(output_file):
                print(f"\nResults saved to {output_file}")
                
            scraper.close()
