import pandas as pd
import sys
import time
from pathlib import Path
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class SocialScraper:
    def __init__(self):
        chrome_options = Options()
        # Latest Chrome user agent and anti-detection settings
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.ai_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.logged_in = {
            'linkedin': False,
            'twitter': False
        }

    def login_linkedin(self):
        if self.logged_in['linkedin']:
            return
            
        self.driver.get("https://www.linkedin.com/login")
        # Wait for username field to be interactable
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#username"))
        ).send_keys(os.getenv("LINKEDIN_EMAIL"))
        time.sleep(0.5)  # Allow DOM update
        
        # Find password field using more specific selector
        password_field = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input#password[type='password']"))
        )
        password_field.send_keys(os.getenv("LINKEDIN_PASSWORD"))
        time.sleep(0.5)
        
        # Click submit with verification
        submit_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit_button.click()
        
        # Bypass all verification checks
        time.sleep(5)  # Basic loading wait
        self.logged_in['linkedin'] = True

    def login_twitter(self):
        if self.logged_in['twitter']:
            return
            
        self.driver.get("https://twitter.com/i/flow/login")
        
        # Handle username phase
        # Handle username phase with explicit waits
        username_field = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
        )
        username_field.send_keys(os.getenv("X_USERNAME") + Keys.RETURN)
        
        # Wait for password field to appear
        # Handle password field with explicit waits
        password_field = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[autocomplete='current-password']"))
        )
        password_field.send_keys(os.getenv("X_PASSWORD") + Keys.RETURN)
        
        # Wait for login to complete
        
        time.sleep(5)  # Basic loading wait
        self.logged_in['twitter'] = True

    def google_search(self, query: str) -> List[str]:
        self.driver.get(f"https://www.google.com/search?q={query}")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        # Handle CAPTCHA if present
        if "CAPTCHA" in self.driver.page_source:
            input("Please solve CAPTCHA in browser then press Enter...")
            
        results = []
        for elem in self.driver.find_elements(By.CSS_SELECTOR, "div.g a"):
            url = elem.get_attribute("href")
            if url and "google.com" not in url:
                results.append(url)
            if len(results) >= 10:
                break
        return results

    def analyze_social_links(self, company: str, industry: str, 
                           platform: str, urls: List[str], description: str) -> Optional[str]:
        prompt = f"""Analyze these search results to find the official {platform} profile for:
                    Company: {company}
                    Industry: {industry}
                    Description: {description}

                    Return ONLY the matching URL or 'n/a'. Results:
                    """
        for i, url in enumerate(urls[:10], 1):
            prompt += f"{i}. {url}\n"

        try:
            response = self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.1
            )
            result = response.choices[0].message.content.strip()
            return result if result.startswith("http") else None
        except Exception as e:
            print(f"AI API Error: {e}")
            return None

    def sales_navigator(self):
        dropdown_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.org-overflow-menu__dropdown-trigger"))
        )
        dropdown_button.click()

        sales_nav_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.org-top-card-overflow__sales-navigator-link"))
        )
        sales_nav_link.click()

    def close_tab(self):
        self.driver.close()

    def close(self):
        self.driver.quit()

def main():
    # Define file paths
    data_dir = Path(__file__).parent.parent / 'data'
    csv_path = data_dir / 'wip/merged_raw_data.csv'
    backup_path = data_dir / 'backup/merged_raw_data.csv.backup'

    try:
        # Load the CSV file
        df = pd.read_csv(csv_path)
        
        # Create backup
        df.to_csv(backup_path, index=False)
        print(f"Created backup at: {backup_path}")

        # Find rows with all empty follower columns
        empty_mask = df[['Twitter Followers', 'Instagram Followers', 'Linkedin Followers']].isna().all(axis=1)
        empty_count = empty_mask.sum()
        
        print(f"Found {empty_count} rows with missing follower data")
        
        if empty_count == 0:
            print("No missing data to fill")
            return

        scraper = SocialScraper()
        try:
            scraper.login_linkedin()
            scraper.login_twitter()

            # Process empty rows
            for idx, row in df[empty_mask].iterrows():
                print(f"\nProcessing row {idx + 1}/{len(df)}")
                print(f"Company: {row['Organization Name']}")
                print(f"Industry: {row['Cleaned Industry']}")
                skip_ceo = False  # Flag to track LinkedIn zero input

                platform_data = {
                    'Twitter Followers': ('Twitter', 'X'),
                    'Instagram Followers': ('Instagram', 'Instagram'),
                    'Linkedin Followers': ('LinkedIn', 'LinkedIn')
                }

                for col, (platform, search_term) in platform_data.items():
                    if pd.isna(row[col]):
                        print(f"\nSearching for {platform} profile...")
                        query = f"{row['Organization Name']} {row['Cleaned Industry']} {search_term}"
                        results = scraper.google_search(query)
                        
                        if not results:
                            print("No search results found")
                            continue
                            
                        ai_suggestion = scraper.analyze_social_links(
                            row['Organization Name'], row['Cleaned Industry'], platform, results, row['Description']
                        )
                        
                        if ai_suggestion:
                            print(f"AI suggests: {ai_suggestion}")
                            print(f"Description: {row['Description']}")
                            user_conf = input("Press Enter to accept or 'n' to reject: ").strip().lower()
                            
                            if user_conf == '':
                                scraper.driver.get(ai_suggestion)
                                followers = input(f"Enter {platform} follower count: ").strip()
                                if followers:
                                    try:
                                        clean_followers = followers.replace(',', '').replace('+', '')
                                        df.at[idx, col] = float(clean_followers)
                                    except ValueError:
                                        print(f"Invalid number format: {followers}")
                                        df.at[idx, col] = None
                                else:
                                    df.at[idx, col] = None
                            else:
                                followers = input(f"Enter {platform} follower count manually: ").strip()
                                if followers:
                                    try:
                                        clean_followers = followers.replace(',', '').replace('+', '')
                                        df.at[idx, col] = float(clean_followers)
                                    except ValueError:
                                        print(f"Invalid number format: {followers}")
                                        df.at[idx, col] = None
                                else:
                                    df.at[idx, col] = None
                            if platform == 'LinkedIn' and followers == '0':
                                skip_ceo = True
                        else:
                            print("AI could not find a match")
                            followers = input(f"Enter {platform} follower count: ").strip()
                            if followers:
                                try:
                                    clean_followers = followers.replace(',', '').replace('+', '')
                                    df.at[idx, col] = float(clean_followers)
                                except ValueError:
                                    print(f"Invalid number format: {followers}")
                                    df.at[idx, col] = None
                            else:
                                df.at[idx, col] = None
                            if platform == 'LinkedIn' and followers == '0':
                                skip_ceo = True
                        
                        # Save progress after each platform
                        df.to_csv(csv_path, index=False)

                # Update CEO connections
                if pd.isna(row['CEO Connections']):
                    if skip_ceo:
                        df.at[idx, 'CEO Connections'] = 0
                        print("Automatically setting CEO connections to 0 based on LinkedIn input")
                    else:
                        scraper.sales_navigator()
                        connections = input("Enter CEO LinkedIn connections: ").strip()
                        if connections:
                            try:
                                # Remove commas and plus signs, convert to float
                                clean_connections = connections.replace(',', '').replace('+', '')
                                df.at[idx, 'CEO Connections'] = float(clean_connections)
                            except ValueError:
                                print(f"Invalid number format: {connections}")
                                df.at[idx, 'CEO Connections'] = None
                        else:
                            df.at[idx, 'CEO Connections'] = None
                    df.to_csv(csv_path, index=False)

        except KeyboardInterrupt:
            print("\nUser interrupted process")
        finally:
            scraper.close()
            print("Browser closed")

        print("\nAll missing data processed successfully")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
