import requests
import json
import os
import csv
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
            'per_page': 50,
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
    seen_bills = set()  # To remove duplicates
    
    for bill in bills:
        # Create unique identifier
        bill_key = f"{bill.get('jurisdiction', {}).get('name', '')}_{bill.get('identifier', '')}"
        if bill_key in seen_bills:
            continue
        seen_bills.add(bill_key)
        
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
    
    # Sort by State, then by Bill_ID
    processed_data.sort(key=lambda x: (x['State'], x['Bill_ID']))
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    fieldnames = ['State', 'Bill_ID', 'Title', 'Status', 'Category', 'Session', 'Updated', 'URL', 'Last_Checked']
    
    with open('data/ai_legislation_bills.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"Processed {len(processed_data)} bills")
    print(f"Data saved to data/ai_legislation_bills.csv")
    
    # Create summary by state
    state_counts = {}
    state_categories = {}
    
    for bill in processed_data:
        state = bill['State']
        if state not in state_counts:
            state_counts[state] = 0
            state_categories[state] = set()
        state_counts[state] += 1
        if bill['Category']:
            state_categories[state].update(bill['Category'].split('; '))
    
    summary_data = []
    for state in sorted(state_counts.keys()):
        summary_data.append({
            'State': state,
            'Bill_Count': state_counts[state],
            'Categories': '; '.join(sorted(state_categories[state]))
        })
    
    with open('data/ai_legislation_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['State', 'Bill_Count', 'Categories'])
        writer.writeheader()
        writer.writerows(summary_data)
    
    print(f"Summary saved to data/ai_legislation_summary.csv")

if __name__ == "__main__":
    process_legislation_data()
