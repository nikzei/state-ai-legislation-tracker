import requests
import pandas as pd
import json
import os
from datetime import datetime

def fetch_ai_legislation():
    """Fetch AI-related bills from OpenStates API"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        raise ValueError("OpenStates API key not found in environment variables")
    
    # Search terms for AI legislation
    search_terms = [
        "artificial intelligence",
        "automated decision",
        "machine learning",
        "algorithmic",
        "deepfake"
    ]
    
    all_bills = []
    
    for term in search_terms:
        url = "https://v3.openstates.org/bills"
        params = {
            'q': term,
            'session': '2025',
            'per_page': 100,
            'include': 'abstracts,actions,sources'
        }
        
        headers = {
            'X-API-KEY': api_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data:
                all_bills.extend(data['results'])
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for term '{term}': {e}")
            continue
    
    return all_bills

def categorize_bill(title, abstract=""):
    """Simple categorization based on keywords"""
    text = (title + " " + abstract).lower()
    
    categories = []
    
    if any(term in text for term in ['healthcare', 'medical', 'health']):
        categories.append('Healthcare')
    if any(term in text for term in ['employment', 'hiring', 'workplace', 'job']):
        categories.append('Employment')
    if any(term in text for term in ['election', 'voting', 'campaign', 'deepfake']):
        categories.append('Elections')
    if any(term in text for term in ['privacy', 'data protection', 'personal information']):
        categories.append('Privacy')
    if any(term in text for term in ['transparency', 'disclosure', 'watermark']):
        categories.append('Transparency')
    if any(term in text for term in ['government', 'agency', 'public sector']):
        categories.append('Government Use')
    if any(term in text for term in ['chatbot', 'bot disclosure']):
        categories.append('Chatbots')
    if any(term in text for term in ['child', 'minor', 'exploitation']):
        categories.append('Child Protection')
    
    return '; '.join(categories) if categories else 'General'

def process_legislation_data():
    """Process raw bill data into tracker format"""
    
    print("Fetching legislation data...")
    bills = fetch_ai_legislation()
    
    if not bills:
        print("No bills found")
        return
    
    processed_data = []
    
    for bill in bills:
        # Get the latest action for status
        latest_action = ""
        if bill.get('actions'):
            latest_action = bill['actions'][0].get('description', '') if bill['actions'] else ''
        
        # Get abstract
        abstract = ""
        if bill.get('abstracts'):
            abstract = bill['abstracts'][0].get('abstract', '') if bill['abstracts'] else ''
        
        processed_bill = {
            'State': bill.get('jurisdiction', {}).get('name', ''),
            'Bill_ID': bill.get('identifier', ''),
            'Title': bill.get('title', ''),
            'Status': latest_action,
            'Category': categorize_bill(bill.get('title', ''), abstract),
            'Session': bill.get('session', ''),
            'Updated': bill.get('updated_at', ''),
            'URL': bill.get('sources', [{}])[0].get('url', '') if bill.get('sources') else '',
            'Last_Checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        processed_data.append(processed_bill)
    
    # Convert to DataFrame and save
    df = pd.DataFrame(processed_data)
    
    # Remove duplicates based on State and Bill_ID
    df = df.drop_duplicates(subset=['State', 'Bill_ID'])
    
    # Sort by State, then by Bill_ID
    df = df.sort_values(['State', 'Bill_ID'])
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/ai_legislation_bills.csv', index=False)
    
    print(f"Processed {len(df)} bills")
    print(f"Data saved to data/ai_legislation_bills.csv")
    
    # Create summary by state
    summary = df.groupby('State').agg({
        'Bill_ID': 'count',
        'Category': lambda x: '; '.join(x.unique())
    }).rename(columns={'Bill_ID': 'Bill_Count', 'Category': 'Categories'}).reset_index()
    
    summary.to_csv('data/ai_legislation_summary.csv', index=False)
    print(f"Summary saved to data/ai_legislation_summary.csv")

if __name__ == "__main__":
    process_legislation_data()
