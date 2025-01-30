# Thesis Project: Analyzing the Impact of Digital Presence on Venture Capital Funding Success in Germany

## Table of Contents

- [Project Overview](#project-overview)
- [Motivation](#motivation)
- [Installation](#installation)
- [Usage](#usage)
- [Data Collection](#data-collection)
- [Data Cleaning](#data-cleaning)
- [Data Analysis](#data-analysis)
- [Data Preprocessing Summary](#data-summary)
- [Results](#results)
- [Additional Notes](#additional-notes)

## Project Overview

This project investigates how an entrepreneur's digital presence influences their success in securing venture capital (VC) funding in Germany. By analyzing data from 761 German startups and conducting interviews with 18 German VCs, the study explores various aspects of digital identity, including professional networks, online reputation, and social media engagement, to understand their correlation with funding outcomes.

## Motivation

In today's digital age, an entrepreneur's online presence can significantly impact their ability to attract investment. This study aims to quantify and qualify the relationship between digital identity metrics and VC funding success, providing insights into the preferences and evaluation criteria of German venture capitalists.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/jacksonly/thesis_project.git
   cd thesis_project
   ```

2. **Set Up a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**  
   Create a `.env` file in the root directory:
   ```ini
   CRUNCHBASE_API_KEY=your_crunchbase_api_key
   SOCIAL_MEDIA_API_KEY=your_social_media_api_key
   ```

## Usage

### Data Collection

```bash
# Crunchbase Scraper
python scraper/crunchbase_scraper.py

# FX Scraper
python scraper/fx_scraper.py

# Social Media Scraper
python scraper/social_scraper.py
```

### Data Cleaning

```bash
python scripts/apply_log_transform.py
python scripts/categorize_industries.py
```

### Data Analysis

```bash
python scripts/analysis/quantitative_analysis.py
python scripts/analysis/qualitative_analysis.py
python scripts/analysis/questionnaire_quantitative_analysis.py
python scripts/analysis/stage_specific_quant_analysis.py
python scripts/analysis/robustness.py
python scripts/analysis/robustness_0_values_trimmed.py
```

## Data Preprocessing Summary

### Data Collection

1. Scraped data from Crunchbase with specific parameters:

   - Headquarters Location: Germany
   - Industries: Web3, Intelligent Systems, Generative AI, Cyber Security, Cloud Security, Cloud Data Services, CivicTech, Business Information Systems, 3D Technology, Android, App, Discovery Application, Performance Management, Apps, Artificial Intelligence (AI), Augmented Reality, Billing, Bitcoin, Browser Extensions, Business Process Automation (BPA), CAD, Chatbot, Cloud Computing, Cloud Management, CMS, Computer Vision, Consumer Applications, Consumer Software, Contact Management, CRM, Cryptocurrency, Data Center, Automation, Data Integration, Data Storage, Data Visualization, Database, Developer APIs, Developer Platform, Developer Tools, DevOps, Document Management, Drone Management, E-Learning, EdTech, Electronic Design Automation (EDA), Embedded Software, Embedded Systems, Enterprise Applications, Enterprise Resource Planning (ERP), Enterprise Software, Facial Recognition, File Sharing, IaaS, Image Recognition, iOS, Linux, Machine Learning, macOS, Marketing Automation, Meeting Software, Metaverse, Mobile Apps, Mobile Payments, MOOC, Natural Language Processing, Open Source, Operating Systems, PaaS, Predictive Analytics, Presentation Software, Presentations, Private Cloud, Productivity Tools, QR Codes, Reading Apps, Retail Technology, Robotic Process Automation (RPA), Robotics, SaaS, Sales Automation, Scheduling, Sex Tech, Simulation, SNS, Social CRM Software, Software Engineering, Speech Recognition, Task Management, Text Analytics, Transaction Processing, Video Conferencing, Virtual Assistant, Virtual Currency, Virtual Desktop, Virtual Goods, Virtual Reality, Virtual World, Virtualization, Web Apps, Web Browsers, Web Development

2. Performed manual social scraping for LinkedIn, X, and Instagram using search engines (Google)

### Data Cleaning and Formatting

3. Manually filled in missing data (0 for startups with no social media presence)
4. Removed duplicates
5. Formatted the "Industries" column to use the first listed industry as "Cleaned Industry"
6. Converted all dates to ISO format (using the first day of the month for missing days, and January for missing months)
7. Scraped historical EUR/USD data from yahoo finance for currency exchange and formatted to ISO
8. Created a dummy variable for CEO LinkedIn connection count (>500 connections)
9. Converted all currencies to EUR using historical data
10. Added "Organization Age" (time between founded date and today, rounded to full years)
11. Split "Headquarters Location" into "Headquarters City" and "Headquarters State"
12. Added "funding_time_months" (last_funding_date – founded_date, truncated to non-negative values)
13. Renamed columns for better handling
14. Coded funding rounds: Pre-Seed as 1, Seed as 2, and Series A as 3

### Feature Engineering

15. Added dummy variables for location and industry
16. Grouped "Cleaned Industry" into broader categories using GICS
17. Added dummy variables for the new industry groupings

### Data Transformation

18. Checked for skewness
19. Applied log transformation to highly skewed data, adding a small epsilon to avoid log(0)
20. Filled 0 for all empty entries (assuming startups with no funding are out of business)

This preprocessing pipeline ensures a clean, structured dataset ready for analysis, with appropriate handling of missing values, categorical variables, and skewed distributions.

## Results

### Hypothesis Testing

See Thesis

### Descriptive Findings

- **Survey Responses:**
  - Professional networks rated high (M=3.89)
  - Social media engagement rated lower (M=2.61)

### Robustness Checks

1. Trimming Top 5% Funding Outliers
2. Excluding Zero-Funding Observations

## Additional Notes

- Use `.gitignore` for sensitive files
- Maintain documentation in code comments
- Regular dependency updates via `requirements.txt`
- Comply with data protection regulations (GDPR)
