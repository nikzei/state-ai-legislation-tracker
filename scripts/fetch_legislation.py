import requests
import json
import os
import csv
from datetime import datetime
import time

def fetch_ai_legislation():
    """Fetch AI-related bills from OpenStates API - simplified working version"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        raise ValueError("OpenStates API key not found in environment variables")
    
    # Simplified search terms that work with OpenStates API
    search_terms = [
        "artificial intelligence",
        "deepfake", 
        "chatbot",
        "algorithmic",
        "automated decision"
    ]
    
    all_bills = []
    
    for term in search_terms:
        print(f"Searching for: {term}")
        
        # Simplified API call that works
        url = "https://v3.openstates.org/bills"
        params = {
            'q': term,
            'per_page': 50  # Reduced from 100
            # Removed 'sort' parameter as it seems to cause 422 errors
        }
        
        headers = {
            'X-API-KEY': api_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 422:
                print(f"  422 error for '{term}' - trying simpler search...")
                # Try without complex terms
                simple_params = {'q': term.split()[0], 'per_page': 20}
                response = requests.get(url, params=simple_params, headers=headers)
            
            if response.status_code == 429:
                print(f"  Rate limited - waiting 30 seconds...")
                time.sleep(30)
                response = requests.get(url, params=params, headers=headers)
            
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data and data['results']:
                bills_found = len(data['results'])
                print(f"  ✓ Found {bills_found} bills for '{term}'")
                all_bills.extend(data['results'])
            else:
                print(f"  No results found for '{term}'")
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error fetching data for term '{term}': {e}")
            continue
        
        # Longer delay between requests to avoid rate limiting
        print(f"  Waiting 5 seconds...")
        time.sleep(5)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total bills collected: {len(all_bills)}")
    return all_bills

def is_ai_related(title, abstract=""):
    """Simple AI detection to filter relevant bills"""
    text = (title + " " + abstract).lower()
    
    # Must contain at least one of these terms
    ai_terms = [
        'artificial intelligence', 'ai ', ' ai', 'a.i.',
        'machine learning', 'deep learning', 'neural network',
        'automated decision', 'algorithmic decision', 'algorithm',
        'chatbot', 'bot ', 'deepfake', 'synthetic media',
        'generative', 'automated system'
    ]
    
    has_ai_term = any(term in text for term in ai_terms)
    
    # Exclude obvious false positives
    exclude_terms = [
        'agriculture', 'farming', 'american indian', 'air quality', 
        'aviation', 'aircraft', 'artificial insemination'
    ]
    
    has_exclude = any(term in text for term in exclude_terms)
    
    return has_ai_term and not has_exclude

def categorize_bill(title, abstract=""):
    """Categorize AI bills by topic"""
    text = (title + " " + abstract).lower()
    
    categories = []
    
    if any(term in text for term in ['healthcare', 'medical', 'health', 'patient']):
        categories.append('Healthcare')
    if any(term in text for term in ['employment', 'hiring', 'workplace', 'job']):
        categories.append('Employment')
    if any(term in text for term in ['election', 'voting', 'campaign', 'deepfake']):
        categories.append('Elections')
    if any(term in text for term in ['privacy', 'data protection', 'personal information']):
        categories.append('Privacy')
    if any(term in text for term in ['transparency', 'disclosure', 'explainable']):
        categories.append('Transparency')
    if any(term in text for term in ['government', 'agency', 'public sector']):
        categories.append('Government Use')
    if any(term in text for term in ['chatbot', 'bot disclosure']):
        categories.append('Chatbots')
    if any(term in text for term in ['child', 'minor', 'student', 'education']):
        categories.append('Child Protection/Education')
    if any(term in text for term in ['bias', 'discrimination', 'fairness']):
        categories.append('Bias/Discrimination')
    
    return '; '.join(categories) if categories else 'General AI'

def get_simple_status(actions):
    """Simple status categorization"""
    if not actions:
        return 'Introduced'
    
    latest_action = actions[0].get('description', '').lower()
    
    if any(term in latest_action for term in ['signed', 'enacted', 'effective']):
        return 'Enacted'
    elif any(term in latest_action for term in ['passed']):
        return 'Passed'
    elif any(term in latest_action for term in ['failed', 'defeated']):
        return 'Failed'
    elif any(term in latest_action for term in ['vetoed']):
        return 'Vetoed'
    else:
        return 'Active'

def process_legislation_data():
    """Process and save AI legislation data"""
    
    print("=== AI LEGISLATION TRACKER ===\n")
    bills = fetch_ai_legislation()
    
    if not bills:
        print("No bills found - check API connection")
        return
    
    print(f"\nFiltering {len(bills)} bills for AI relevance...")
    processed_data = []
    seen_bills = set()
    filtered_out = 0
    
    for bill in bills:
        # Remove duplicates
        bill_key = f"{bill.get('jurisdiction', {}).get('name', '')}_{bill.get('identifier', '')}"
        if bill_key in seen_bills:
            continue
        seen_bills.add(bill_key)
        
        # Check if actually AI-related
        title = bill.get('title', '')
        abstract = ""
        if bill.get('abstracts'):
            abstract = bill['abstracts'][0].get('abstract', '') if bill['abstracts'] else ''
        
        if not is_ai_related(title, abstract):
            filtered_out += 1
            continue
        
        # Process the bill
        actions = bill.get('actions', [])
        
        processed_bill = {
            'State': bill.get('jurisdiction', {}).get('name', ''),
            'Bill_ID': bill.get('identifier', ''),
            'Title': title,
            'Status': get_simple_status(actions),
            'Category': categorize_bill(title, abstract),
            'Session': bill.get('session', ''),
            'Updated': bill.get('updated_at', ''),
            'URL': bill.get('sources', [{}])[0].get('url', '') if bill.get('sources') else '',
            'Last_Checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        processed_data.append(processed_bill)
    
    print(f"✓ Filtered out {filtered_out} non-AI bills")
    print(f"✓ Processing {len(processed_data)} AI-related bills")
    
    if not processed_data:
        print("No AI-related bills found after filtering")
        return
    
    # Sort by State, then Bill_ID
    processed_data.sort(key=lambda x: (x['State'], x['Bill_ID']))
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save main data file
    fieldnames = ['State', 'Bill_ID', 'Title', 'Status', 'Category', 'Session', 'Updated', 'URL', 'Last_Checked']
    
    with open('data/ai_legislation_bills.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"✓ Saved {len(processed_data)} bills to data/ai_legislation_bills.csv")
    
    # Create summary by state
    state_summary = {}
    for bill in processed_data:
        state = bill['State']
        if state not in state_summary:
            state_summary[state] = {
                'Total_Bills': 0,
                'Enacted': 0,
                'Active': 0,
                'Categories': set()
            }
        
        state_summary[state]['Total_Bills'] += 1
        state_summary[state]['Categories'].add(bill['Category'])
        
        if bill['Status'] == 'Enacted':
            state_summary[state]['Enacted'] += 1
        elif bill['Status'] in ['Active', 'Passed']:
            state_summary[state]['Active'] += 1
    
    # Create summary data
    summary_data = []
    for state in sorted(state_summary.keys()):
        data = state_summary[state]
        framework_status = 'Comprehensive' if data['Enacted'] >= 2 else 'Some Activity' if data['Total_Bills'] >= 2 else 'Minimal'
        
        summary_data.append({
            'State': state,
            'Total_Bills': data['Total_Bills'],
            'Enacted': data['Enacted'],
            'Active_Pending': data['Active'],
            'Categories': '; '.join(sorted([cat for cat in data['Categories'] if cat])),
            'Framework_Status': framework_status
        })
    
    # Sort by most active
    summary_data.sort(key=lambda x: x['Total_Bills'], reverse=True)
    
    with open('data/ai_legislation_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        summary_fieldnames = ['State', 'Total_Bills', 'Enacted', 'Active_Pending', 'Categories', 'Framework_Status']
        writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
        writer.writeheader()
        writer.writerows(summary_data)
    
    print(f"✓ Saved state summary to data/ai_legislation_summary.csv")
    print(f"\n=== SUCCESS ===")
    print(f"Created 2 data files with {len(processed_data)} AI bills from {len(state_summary)} states")

if __name__ == "__main__":
    process_legislation_data()
