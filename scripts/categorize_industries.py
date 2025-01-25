import pandas as pd
import argparse
import logging
import sys
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

INDUSTRY_MAPPING = {
    '3D Printing': 'Information Technology',
    'SaaS': 'Information Technology',
    '3D Technology': 'Information Technology',
    'Accounting': 'Financials',
    'Ad Exchange': 'Communication Services',
    'Ad Network': 'Communication Services',
    'Ad Server': 'Communication Services',
    'Ad Targeting': 'Communication Services',
    'Advanced Materials': 'Materials',
    'Advertising': 'Communication Services',
    'Advertising Platforms': 'Communication Services',
    'Advice': 'Financials',
    'Aerospace': 'Industrials',
    'Affiliate Marketing': 'Communication Services',
    'Agriculture': 'Consumer Staples',
    'Agtech': 'Information Technology',
    'Ai': 'Information Technology',
    'AI': 'Information Technology',
    'Air Transportation': 'Industrials',
    'Analytics': 'Information Technology',
    'Android': 'Information Technology',
    'Angel Investment': 'Financials',
    'Application Performance Management': 'Information Technology',
    'Apps': 'Information Technology',
    'Architecture': 'Industrials',
    'Art': 'Communication Services',
    'Asset Management': 'Financials',
    'Assisted Living': 'Health Care',
    'Assistive Technology': 'Health Care',
    'Audio': 'Communication Services',
    'Augmented Reality': 'Information Technology',
    'Auto Insurance': 'Financials',
    'Automotive': 'Consumer Discretionary',
    'Autonomous Vehicles': 'Consumer Discretionary',
    'B2B': 'Industrials',
    'B2C': 'Consumer Discretionary',
    'Banking': 'Financials',
    'Beauty': 'Consumer Staples',
    'Big Data': 'Information Technology',
    'Billing': 'Information Technology',
    'Bioinformatics': 'Health Care',
    'Biotechnology': 'Health Care',
    'Bitcoin': 'Financials',
    'Blockchain': 'Information Technology',
    'Boating': 'Consumer Discretionary',
    'Brewing': 'Consumer Staples',
    'Broadcasting': 'Communication Services',
    'Browser Extensions': 'Information Technology',
    'Business Development': 'Industrials',
    'Business Information Systems': 'Information Technology',
    'Business Intelligence': 'Information Technology',
    'Business Process Automation (Bpa)': 'Information Technology',
    'Cad': 'Information Technology',
    'Carbon Capture': 'Utilities',
    'Career Planning': 'Industrials',
    'Casual Games': 'Communication Services',
    'Catering': 'Consumer Discretionary',
    'Charging Infrastructure': 'Utilities',
    'Chemical': 'Materials',
    'Civil Engineering': 'Industrials',
    'Clean Energy': 'Utilities',
    'Cleantech': 'Utilities',
    'Clinical Trials': 'Health Care',
    'Cloud Computing': 'Information Technology',
    'Cloud Data Services': 'Information Technology',
    'Cloud Infrastructure': 'Information Technology',
    'Cloud Management': 'Information Technology',
    'Cloud Security': 'Information Technology',
    'Cms': 'Information Technology',
    'Coffee': 'Consumer Staples',
    'Collaboration': 'Information Technology',
    'Commercial': 'Real Estate',
    'Commercial Real Estate': 'Real Estate',
    'Communication Hardware': 'Information Technology',
    'Communities': 'Communication Services',
    'Compliance': 'Industrials',
    'Computer': 'Information Technology',
    'Computer Vision': 'Information Technology',
    'Concerts': 'Communication Services',
    'Construction': 'Industrials',
    'Consulting': 'Industrials',
    'Consumer': 'Consumer Discretionary',
    'Consumer Applications': 'Information Technology',
    'Consumer Electronics': 'Consumer Discretionary',
    'Consumer Software': 'Information Technology',
    'Content': 'Communication Services',
    'Content Creators': 'Communication Services',
    'Content Marketing': 'Communication Services',
    'Continuing Education': 'Consumer Discretionary',
    'Cooking': 'Consumer Discretionary',
    'Corporate Training': 'Industrials',
    'Cosmetics': 'Consumer Staples',
    'Coworking': 'Real Estate',
    'Credit Cards': 'Financials',
    'Crm': 'Information Technology',
    'Crowdfunding': 'Financials',
    'Cryptocurrency': 'Financials',
    'Customer Service': 'Industrials',
    'Cyber Security': 'Information Technology',
    'Data Center': 'Information Technology',
    'Data Collection And Labeling': 'Information Technology',
    'Data Integration': 'Information Technology',
    'Data Management': 'Information Technology',
    'Data Storage': 'Information Technology',
    'Data Visualization': 'Information Technology',
    'Database': 'Information Technology',
    'Dating': 'Communication Services',
    'Debit Cards': 'Financials',
    'Debt Collections': 'Financials',
    'Decentralized Finance (Defi)': 'Financials',
    'Delivery': 'Industrials',
    'Delivery Service': 'Industrials',
    'Desktop Apps': 'Information Technology',
    'Developer Apis': 'Information Technology',
    'Developer Platform': 'Information Technology',
    'Developer Tools': 'Information Technology',
    'Devops': 'Information Technology',
    'Diabetes': 'Health Care',
    'Digital Entertainment': 'Communication Services',
    'Digital Marketing': 'Communication Services',
    'Digital Media': 'Communication Services',
    'Direct Sales': 'Consumer Discretionary',
    'Diving': 'Consumer Discretionary',
    'Document Management': 'Information Technology',
    'Drones': 'Industrials',
    'E-Commerce': 'Consumer Discretionary',
    'E-Commerce Platforms': 'Information Technology',
    'E-Learning': 'Consumer Discretionary',
    'Edtech': 'Information Technology',
    'Education': 'Consumer Discretionary',
    'Edutainment': 'Communication Services',
    'Elder Care': 'Health Care',
    'Elderly': 'Health Care',
    'Electric Vehicle': 'Consumer Discretionary',
    'Electronic Health Record (Ehr)': 'Health Care',
    'Electronics': 'Information Technology',
    'Email': 'Information Technology',
    'Embedded Software': 'Information Technology',
    'Embedded Systems': 'Information Technology',
    'Employee Benefits': 'Industrials',
    'Employment': 'Industrials',
    'Energy': 'Energy',
    'Energy Efficiency': 'Utilities',
    'Energy Management': 'Utilities',
    'Energy Storage': 'Utilities',
    'Enterprise': 'Information Technology',
    'Enterprise Applications': 'Information Technology',
    'Enterprise Resource Planning (Erp)': 'Information Technology',
    'Enterprise Software': 'Information Technology',
    'Environmental Consulting': 'Industrials',
    'Esports': 'Communication Services',
    'Event Management': 'Communication Services',
    'Events': 'Communication Services',
    'Eyewear': 'Consumer Discretionary',
    'Facility Management': 'Real Estate',
    'Farming': 'Consumer Staples',
    'Fashion': 'Consumer Discretionary',
    'Fast-Moving Consumer Goods': 'Consumer Staples',
    'Fertility': 'Health Care',
    'Film': 'Communication Services',
    'Finance': 'Financials',
    'Financial Services': 'Financials',
    'Fintech': 'Financials',
    'Food And Beverage': 'Consumer Staples',
    'Food Delivery': 'Consumer Discretionary',
    'Fossil Fuels': 'Energy',
    'Fraud Detection': 'Information Technology',
    'Freight Service': 'Industrials',
    'Funding Platform': 'Financials',
    'Gamification': 'Information Technology',
    'Gaming': 'Communication Services',
    'Generative Ai': 'Information Technology',
    'Geospatial': 'Information Technology',
    'Govtech': 'Information Technology',
    'Green Consumer Goods': 'Consumer Staples',
    'Greentech': 'Utilities',
    'Grocery': 'Consumer Staples',
    'Hardware': 'Information Technology',
    'Health Care': 'Health Care',
    'Health Diagnostics': 'Health Care',
    'Higher Education': 'Consumer Discretionary',
    'Home Health Care': 'Health Care',
    'Home Renovation': 'Consumer Discretionary',
    'Hospital': 'Health Care',
    'Hospitality': 'Consumer Discretionary',
    'Hotel': 'Consumer Discretionary',
    'Human Resources': 'Industrials',
    'Iaas': 'Information Technology',
    'Identity Management': 'Information Technology',
    'Industrial': 'Industrials',
    'Industrial Automation': 'Industrials',
    'Industrial Manufacturing': 'Industrials',
    'Information Services': 'Information Technology',
    'Information Technology': 'Information Technology',
    'Infrastructure': 'Industrials',
    'Innovation Management': 'Information Technology',
    'Insurance': 'Financials',
    'Insurtech': 'Financials',
    'Intelligent Systems': 'Information Technology',
    'Internet': 'Communication Services',
    'Internet Of Things': 'Information Technology',
    'Ios': 'Information Technology',
    'It Infrastructure': 'Information Technology',
    'It Management': 'Information Technology',
    'Knowledge Management': 'Information Technology',
    'Lead Generation': 'Communication Services',
    'Lead Management': 'Communication Services',
    'Legal': 'Industrials',
    'Legal Tech': 'Information Technology',
    'Lending': 'Financials',
    'Lifestyle': 'Consumer Discretionary',
    'Logistics': 'Industrials',
    'Machine Learning': 'Information Technology',
    'Machinery Manufacturing': 'Industrials',
    'Management Information Systems': 'Information Technology',
    'Manufacturing': 'Industrials',
    'Mapping Services': 'Information Technology',
    'Market Research': 'Communication Services',
    'Marketing': 'Communication Services',
    'Marketplace': 'Consumer Discretionary',
    'Media And Entertainment': 'Communication Services',
    'Medical': 'Health Care',
    'Medical Device': 'Health Care',
    'Meeting Software': 'Information Technology',
    'Mental Health': 'Health Care',
    'Metaverse': 'Information Technology',
    'Mobile': 'Information Technology',
    'Mobile Advertising': 'Communication Services',
    'Mobile Apps': 'Information Technology',
    'Mobile Payments': 'Information Technology',
    'Music': 'Communication Services',
    'Music Education': 'Consumer Discretionary',
    'Natural Language Processing': 'Information Technology',
    'Navigation': 'Information Technology',
    'Network Hardware': 'Information Technology',
    'Network Security': 'Information Technology',
    'Neuroscience': 'Health Care',
    'News': 'Communication Services',
    'Non-Fungible Token (Nft)': 'Information Technology',
    'Nursing And Residential Care': 'Health Care',
    'Online Games': 'Communication Services',
    'Open Source': 'Information Technology',
    'Outsourcing': 'Industrials',
    'Paas': 'Information Technology',
    'Packaging Services': 'Materials',
    'Payments': 'Financials',
    'Personal Development': 'Consumer Discretionary',
    'Personalization': 'Information Technology',
    'Pet': 'Consumer Discretionary',
    'Podcast': 'Communication Services',
    'Point Of Sale': 'Information Technology',
    'Privacy': 'Information Technology',
    'Procurement': 'Industrials',
    'Product Management': 'Information Technology',
    'Product Research': 'Industrials',
    'Productivity Tools': 'Information Technology',
    'Property Management': 'Real Estate',
    'Proptech': 'Real Estate',
    'Public Safety': 'Industrials',
    'Publishing': 'Communication Services',
    'Quantum Computing': 'Information Technology',
    'Railroad': 'Industrials',
    'Reading Apps': 'Information Technology',
    'Real Estate': 'Real Estate',
    'Real Time': 'Information Technology',
    'Recruiting': 'Industrials',
    'Recycling': 'Industrials',
    'Renewable Energy': 'Utilities',
    'Rental': 'Real Estate',
    'Restaurants': 'Consumer Discretionary',
    'Retail': 'Consumer Discretionary',
    'Retail Technology': 'Information Technology',
    'Ride Sharing': 'Industrials',
    'Robotic Process Automation (Rpa)': 'Information Technology',
    'Robotics': 'Information Technology',
    'Saas': 'Information Technology',
    'Sales': 'Industrials',
    'Sales Automation': 'Information Technology',
    'Sales Enablement': 'Information Technology',
    'Search Engine': 'Information Technology',
    'Semantic Search': 'Information Technology',
    'Semiconductor': 'Information Technology',
    'Service Industry': 'Industrials',
    'Sharing Economy': 'Industrials',
    'Shipping': 'Industrials',
    'Simulation': 'Information Technology',
    'Skill Assessment': 'Industrials',
    'Small And Medium Businesses': 'Industrials',
    'Smart Home': 'Consumer Discretionary',
    'Social': 'Communication Services',
    'Social Crm': 'Information Technology',
    'Social Impact': 'Industrials',
    'Social Media': 'Communication Services',
    'Social Network': 'Communication Services',
    'Software': 'Information Technology',
    'Software Engineering': 'Information Technology',
    'Sports': 'Communication Services',
    'Stem Education': 'Consumer Discretionary',
    'Supply Chain Management': 'Industrials',
    'Sustainability': 'Industrials',
    'Telecommunications': 'Communication Services',
    'Telehealth': 'Health Care',
    'Tourism': 'Consumer Discretionary',
    'Trading Platform': 'Financials',
    'Training': 'Industrials',
    'Transportation': 'Industrials',
    'Travel': 'Consumer Discretionary',
    'Travel Accommodations': 'Consumer Discretionary',
    'Veterinary': 'Health Care',
    'Video': 'Communication Services',
    'Video On Demand': 'Communication Services',
    'Virtual Reality': 'Information Technology',
    'Virtual Workforce': 'Information Technology',
    'Virtualization': 'Information Technology',
    'Water': 'Utilities',
    'Web Apps': 'Information Technology',
    'Web Browsers': 'Information Technology',
    'Web Development': 'Information Technology',
    'Web3': 'Information Technology',
    'Wellness': 'Consumer Discretionary'
}

def load_data(input_path):
    """Load CSV data with proper error handling"""
    try:
        df = pd.read_csv(input_path)
        logging.info(f"Successfully loaded data from {input_path}")
        return df
    except Exception as e:
        logging.error(f"Failed to load input file: {str(e)}")
        sys.exit(1)

def categorize_industries(df):
    """Add industry categorization column"""
    try:
        # Create new column by mapping industries
        df['industry'] = df['Industries'].apply(map_single_industry)
        
        # Move column next to 'Industries'
        cols = df.columns.tolist()
        industries_idx = cols.index('Industries')
        cols.insert(industries_idx + 1, cols.pop(cols.index('industry')))
        
        return df[cols]
    except KeyError as e:
        logging.error(f"Missing required column: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error during categorization: {str(e)}")
        sys.exit(1)

def map_single_industry(industries_str):
    """Map a single organization's industries to category"""
    if pd.isna(industries_str):
        return 'Unknown'
        
    industries = [i.strip() for i in str(industries_str).split(',')]
    
    # Check for custom categories first
    for industry in industries:
        if industry in ['Blockchain', 'Web3', 'NFT']:
            return 'Web3/Blockchain'
    
    # Check main mapping
    for industry in industries:
        if industry in INDUSTRY_MAPPING:
            return INDUSTRY_MAPPING[industry]
    
    return 'Other'

def save_data(df, output_path):
    """Save processed data to CSV"""
    try:
        df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)
        logging.info(f"Successfully saved categorized data to {output_path}")
    except Exception as e:
        logging.error(f"Failed to save output file: {str(e)}")
        sys.exit(1)

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Categorize startup industries using GICS framework')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    args = parser.parse_args()
    
    logging.info("Starting industry categorization process")
    df = load_data(args.input)
    categorized_df = categorize_industries(df)
    save_data(categorized_df, args.output)
    logging.info("Industry categorization completed successfully")

if __name__ == "__main__":
    main()
