Below is a step-by-step breakdown (“atomic” steps) for a junior developer to integrate all your requirements. This outline provides a high-level view of what to build, in what order, and how each piece interacts. No actual code, just conceptual guidance with occasional pseudocode to illustrate the flow.

1. Project Setup
   1. Directory Structure
      • project_root/
      • data/
      • merged_raw_data.csv (the CSV you’re processing)
      • merged_raw_data.csv.backup (the backup)
      • scripts/
      • main_script.py (the primary script orchestrating everything)
      • auth.py (handles login details to LinkedIn, X/Twitter)
      • search_and_ai.py (handles Google searches, AI calls)
      • .env (contains credentials for LinkedIn, X, etc.)
   2. Environment Setup
      • Use python-dotenv (or a similar library) to load environment variables from .env.
      • Example environment variables in .env:

LINKEDIN_EMAIL=your_email_here
LINKEDIN_PASSWORD=your_password_here
X_USERNAME=your_x_username
X_PASSWORD=your_x_password
OPENAI_API_KEY=your_api_key

    3.	Dependencies
    •	Selenium (for web automation)
    •	pandas (CSV reading/writing)
    •	requests or aiohttp (in case you use AI APIs)
    •	beautifulsoup4 (optional for parsing, if you do direct HTML parsing)
    •	openai (or any other LLM client library, depending on your chosen AI provider)
    •	Possibly python-dotenv for environment variable handling.

2. Handling Logins (LinkedIn & X)

   1. Load Credentials from .env
      • linkedin_email = os.getenv("LINKEDIN_EMAIL")
      • linkedin_password = os.getenv("LINKEDIN_PASSWORD")
      • x_username = os.getenv("X_USERNAME")
      • x_password = os.getenv("X_PASSWORD")
   2. Selenium Browser Setup
      • Initiate a webdriver instance (e.g., Chrome or Firefox) with your chosen WebDriver.
      • Configure any desired options (headless mode, user-agent string, etc. if needed).
   3. Login to LinkedIn
      • Use Selenium to go to https://www.linkedin.com/login.
      • Locate username and password fields, type the credentials with slight random delays to appear humanlike.
      • Click the “Sign In” button.
      • Wait for login to complete (e.g., wait until a known element on the homepage is present).
   4. Login to X (Twitter)
      • Similar process: go to https://twitter.com/login (or x.com/login).
      • Input credentials, use slight random delays, confirm login success.

   Note: If you need to maintain the sessions across searches, keep the same Selenium browser window open throughout the script’s runtime.

3. Iterating Through the CSV
   1. Load CSV
      • df = pd.read_csv("data/merged_raw_data.csv")
   2. Create Backup
      • Immediately create a backup to merged_raw_data.csv.backup.
   3. Identify Missing Rows
      • Find rows where Twitter Followers, Instagram Followers, and LinkedIn Followers are empty/NaN:

empty_mask = df[['Twitter Followers', 'Instagram Followers', 'Linkedin Followers']].isna().all(axis=1)

    •	Sum and iterate over those rows for processing.

4. Searching for the Social Accounts

   1. Construct Search Queries
      • For each missing social handle (Instagram, X, LinkedIn), build a query string like:
      • "{company_name} {industry} Instagram"
      • "{company_name} {industry} X"
      • "{company_name} {industry} LinkedIn"
      • Each platform will have its own query.
   2. Perform Google Search
      • Option A: Use Selenium to navigate to google.com, type in the query, and scrape the results.
      • This can be more prone to being blocked by Google. You may need random sleeps or humanlike interactions.
      • Option B: Use a free search engine alternative or a public API (if you find one) to avoid blocking.
      • Parse the top 10 results (URLs, titles, snippets).
   3. Collect the Top 10 Results
      • If using Selenium, you might do something like:
      • Wait for results to load.
      • Gather the URLs (e.g., from the search result elements).
      • Store them in a list: results = [url_1, url_2, ..., url_10].

5. AI Analysis to Identify the Correct Link
   1. Prepare Prompt
      • Provide the list of top 10 URLs, along with context (company name, industry) to the LLM.
      • Example prompt structure:

"Company name: {company_name}
Industry: {industry}
Social Media Platform Sought: Instagram
Here are the top 10 URLs from Google search:

1.  {url_1}
2.  {url_2}
    ...
3.  {url_10}

Which one is the official Instagram link for this company?
If none seems correct, return 'n/a'."

    2.	Call External LLM
    •	Use the library for your chosen LLM, passing the prompt.
    •	Receive the response (a “best guess” link or n/a).
    3.	Interpret LLM Response
    •	If the LLM returns something that looks like a URL, store it in a variable (e.g., found_url).
    •	If the LLM returns “n/a”, we’ll handle that in the user interaction step.

6. User Confirmation and Fallback
   1. Prompt the User
      • Show the guessed URL to the user:

"The AI suggests this Instagram link: {found_url}
Press 'Enter' to confirm or type 'n' if it's not correct."

    2.	User Response Handling
    •	If user presses Enter: proceed with that URL.
    •	If user types ‘n’ (or anything else) to disagree:
    •	Per your requirement, do not override the URL with a manual input.
    •	Instead, proceed to ask the user for the follower count.
    •	This implies you’re done searching for the URL and the user will just manually fill in the follower count for that row.
    3.	If AI Returned ‘n/a’
    •	Prompt the user:

"The AI could not find a likely link. Please type the correct link or press Enter to leave it blank."

    •	If the user provides a link, store that link. If empty, remain blank.

7. Navigating to the Social Page (LinkedIn, X, Instagram)
   1. Open Link in Selenium (if user confirmed the URL or provided a custom one):
      • driver.get(found_url)
   2. Allow the User to See the Page
      • The user will visually confirm the page and read off the follower count.
   3. Ask the User for Follower Count
      • Input prompt:

"Please enter follower count for this page.
Press Enter if unknown."

    4.	Update CSV
    •	Once the user inputs the follower count, set it in the DataFrame column.
    •	df.at[idx, 'Instagram Followers'] = user_follower_input

8. LinkedIn Sales Navigator Option

   1. While on the Company’s LinkedIn Page
      • Provide an option: “Open in Sales Navigator?”
      • If “yes,” click the relevant button/link or follow the Sales Navigator URL pattern:
      • Example URL might be https://www.linkedin.com/sales/company/1234567/ (depends on how LinkedIn organizes its pages).
      • Let the user manually verify additional data if needed.
   2. User Proceeds or Skips
      • If user wants to see it on Sales Navigator, navigate there.
      • If not, skip directly to the follower count prompt.

9. Handling Multiple Potential Matches / Rebrands

   1. AI Decision
      • The LLM prompt already includes instructions to pick the “most likely” handle.
   2. If Rebranded or Multiple Handles
      • The AI might detect domain-level hints (e.g., official website references, brand keywords).
      • The user can override or confirm the AI’s suggestion if it’s wrong.
   3. User Intervention
      • Because the process is partially automated, the user still has the final say to confirm or reject.

10. Save Progress and Move to Next Row
    1. Save After Each Row
       • After you finish (either got a link from AI or n/a, then user follower count), call:

df.to_csv("data/merged_raw_data.csv", index=False)

    2.	Move to Next Row
    •	Continue until all rows with missing data are processed.

11. Edge Cases & Best Practices
    1.  Interruptions
        • If the user presses Ctrl+C or some error occurs, ensure you save the CSV before exiting:

try:

# main logic

except KeyboardInterrupt:
df.to_csv("data/merged_raw_data.csv", index=False)
sys.exit(1)
except Exception as e:
handle_error(e)
sys.exit(1)

    2.	Google Blocks / Captchas
    •	Possibly add random delays, or consider an alternative API for searching if you run into captchas often.
    3.	Multiple Social Platforms
    •	Repeat the same process for Instagram, X, and LinkedIn within each row.

12. Summary of the Flow in Pseudocode

load_env()

# Initialize Selenium WebDriver

driver = start_selenium_driver()

login_linkedin(driver, linkedin_email, linkedin_password)
login_x(driver, x_username, x_password)

df = pd.read_csv("merged_raw_data.csv")
backup_csv(df) # e.g., copy to merged_raw_data.csv.backup

missing_rows = identify_missing_socials(df) # returns index of rows with no data

for idx in missing_rows:
row = df.loc[idx]

    # For each social platform we want to find (Instagram, X, LinkedIn):
    for platform in ['Instagram', 'X', 'LinkedIn']:
        if df.at[idx, f'{platform} Followers'] is NaN:
            query = f"{row.company_name} {row.industry} {platform}"
            results = google_search(driver, query, top_n=10)

            found_url = ai_guess_best_link(
                company_name=row.company_name,
                industry=row.industry,
                platform=platform,
                results=results
            )

            # show found_url to user
            user_response = ask_user_confirm(found_url)

            if user_response == "confirm":
                # open link in Selenium
                driver.get(found_url)

                # possibly open Sales Navigator if LinkedIn
                # prompt user "Open sales nav? (y/n)"

                # user inputs follower count
                follower_count = input("Enter follower count:")
                df.at[idx, f'{platform} Followers'] = follower_count

            elif user_response == "reject":
                # user said AI is wrong
                # we do NOT override the URL with manual entry
                # user just manually enters follower count
                follower_count = input("Enter follower count:")
                df.at[idx, f'{platform} Followers'] = follower_count

            elif found_url == 'n/a':
                # user must enter a link or skip
                user_link = input("AI found nothing. Enter link or leave blank:")
                if user_link != "":
                    driver.get(user_link)

                follower_count = input("Enter follower count:")
                df.at[idx, f'{platform} Followers'] = follower_count

            # save after each update
            df.to_csv("merged_raw_data.csv", index=False)

print("Processing complete.")

Final Notes for the Junior Developer
• Testing: Make sure you test each segment individually (login steps, searching, AI prompt, CSV updates) to isolate bugs.
• Rate Limits: If using an external LLM API, watch out for rate limits. Consider adding short waits or handling errors if you exceed them.
• Maintenance: Keep an eye on Selenium if Google or LinkedIn changes their layouts or if you encounter captchas. You may need to adapt your approach or switch to an API-based search solution.

Following these steps should let you implement the script in a structured, maintainable way.
