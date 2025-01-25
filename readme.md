# Introduction

## Data Preprocessing Summary

### Data Collection

1. Scraped data from Crunchbase with specific parameters:

   - Headquarters Location: Germany
   - Industries: Web3, Intelligent Systems, Generative AI, Cyber Security, Cloud Security, Cloud Data Services, CivicTech, Business Information Systems, 3D Technology, Android, App, Discovery Application, Performance Management, Apps, Artificial Intelligence (AI), Augmented Reality, Billing, Bitcoin, Browser Extensions, Business Process Automation (BPA), CAD, Chatbot, Cloud Computing, Cloud Management, CMS, Computer Vision, Consumer Applications, Consumer Software, Contact Management, CRM, Cryptocurrency, Data Center, Automation, Data Integration, Data Storage, Data Visualization, Database, Developer APIs, Developer Platform, Developer Tools, DevOps, Document Management, Drone Management, E-Learning, EdTech, Electronic Design Automation (EDA), Embedded Software, Embedded Systems, Enterprise Applications, Enterprise Resource Planning (ERP), Enterprise Software, Facial Recognition, File Sharing, IaaS, Image Recognition, iOS, Linux, Machine Learning, macOS, Marketing Automation, Meeting Software, Metaverse, Mobile Apps, Mobile Payments, MOOC, Natural Language Processing, Open Source, Operating Systems, PaaS, Predictive Analytics, Presentation Software, Presentations, Private Cloud, Productivity Tools, QR Codes, Reading Apps, Retail Technology, Robotic Process Automation (RPA), Robotics, SaaS, Sales Automation, Scheduling, Sex Tech, Simulation, SNS, Social CRM Software, Software Engineering, Speech Recognition, Task Management, Text Analytics, Transaction Processing, Video Conferencing, Virtual Assistant, Virtual Currency, Virtual Desktop, Virtual Goods, Virtual Reality, Virtual World, Virtualization, Web Apps, Web Browsers, Web Development

2. Performed social scraping for LinkedIn, X, and Instagram using search engines (Google)

### Data Cleaning and Formatting

3. Manually filled in missing data (NaN for startups with no social media presence)
4. Removed duplicates
5. Formatted the "industries" column to use the first listed industry as "Cleaned Industry"
6. Converted all dates to ISO format (using the first day of the month for missing days, and January for missing months)
7. Scraped historical EUR/USD data for currency exchange and formatted to ISO
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
