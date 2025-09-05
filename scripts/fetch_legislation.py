import requests
import json
import os
import csv
from datetime import datetime
import time

def fetch_ai_legislation():
    """Fetch AI-related bills from OpenStates API - working version"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        raise ValueError("OpenStates API key not found in environment variables")
    
    headers = {'X-API-KEY': api_key}
    
    # AI-related search terms that work
    search_terms = [
        "AI",
        "artificial intelligence", 
        "deepfake",
        "chatbot",
        "algorithmic",
        "automated decision",
        "machine learning",
        "algorithm bias"
    ]
    
    all_bills = []
    
    print("=== AI LEGISLATION TRACKER ===\n")
    
    for term in search_terms:
        print(f"Searching for: '{term}'")
        
        url = "https://v3.openstates.org/bills"
        params = {
            'q': term,  # This is required!
            'per_page': 50
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and data['results']:
                bills_found = len(data['results'])
                print(f"  ✓ Found {bills_found} bills")
                all_bills.extend(data['results'])
                
                # Check for additional pages
                page = 1
                while 'next' in data and data['next'] and page < 3:  # Limit to 3 pages per term
                    page += 1
                    print(f"  Getting page {page}...")
                    
                    next_response = requests.get(data['next'], headers=headers)
                    next_response.raise_for_status()
                    data = next_response.json()
                    
                    if 'results' in data and data['results']:
                        additional_bills = len(data['results'])
                        print(f"  ✓ Found {additional_bills} more bills")
                        all_bills.extend(data['results'])
                    
                    time.sleep(1)  # Be nice to the API
            else:
                print(f"  No results for '{term}'")
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error for '{term}': {e}")
            continue
        
        time.sleep(2)  # Pause between search terms
    
    print(f"\n=== SUMMARY ===")
    print(f"Total bills collected: {len(all_bills)}")
    return all_bills

def is_ai_related(title, abstract=""):
    """Filter for truly AI-related bills"""
    text = (title + " " + abstract).lower()
    
    # Strong AI indicators
    ai_terms = [
        'artificial intelligence', 'ai ', ' ai', 'a.i.',
        'machine learning', 'deep learning', 'neural network',
        'automated decision', 'algorithmic decision', 'algorithm',
        'chatbot', 'bot ', 'deepfake', 'synthetic media',
        'generative ai', 'large language model'
    ]
    
    has_ai_term = any(term in text for term in ai_terms)
    
    # Exclude false positives
    exclude_terms = [
        'agriculture', 'farming', 'american indian', 'air quality', 
        'aviation', 'aircraft', 'artificial insemination', 'aid to families'
    ]
    
    has_exclude = any(term in text for term in exclude_terms)
    
    return has_ai_term and not has_exclude

def categorize_bill(title, abstract=""):
    """Categorize AI bills by primary focus area"""
    text = (title + " " + abstract).lower()
    
    categories = []
    
    if any(term in text for term in ['health', 'medical', 'patient', 'clinical', 'healthcare']):
        categories.append('Healthcare')
    if any(term in text for term in ['employ', 'hiring', 'workplace', 'job', 'worker']):
        categories.append('Employment')
    if any(term in text for term in ['election', 'voting', 'campaign', 'political', 'deepfake']):
        categories.append('Elections')
    if any(term in text for term in ['privacy', 'data protection', 'personal information']):
        categories.append('Privacy')
    if any(term in text for term in ['transparency', 'disclosure', 'explainable', 'audit']):
        categories.append('Transparency')
    if any(term in text for term in ['government', 'agency', 'public', 'state']):
        categories.append('Government Use')
    if any(term in text for term in ['chatbot', 'bot disclosure', 'conversational']):
        categories.append('Chatbots')
    if any(term in text for term in ['child', 'minor', 'student', 'education', 'school']):
        categories.append('Education/Child Protection')
    if any(term in text for term in ['bias', 'discrimination', 'fairness', 'civil rights']):
        categories.append('Bias/Discrimination')
    if any(term in text for term in ['financial', 'banking', 'credit', 'lending', 'insurance']):
        categories.append('Financial Services')
    if any(term in text for term in ['criminal', 'law enforcement', 'police', 'surveillance']):
        categories.append('Criminal Justice')
    
    return '; '.join(categories) if categories else 'General AI'

def get_bill_status(actions):
    """Determine current status from actions"""
    if not actions:
        return 'Introduced'
    
    latest_action = actions[0].get('description', '').lower()
    
    if any(term in latest_action for term in ['signed', 'enacted', 'effective', 'chaptered']):
        return 'Enacted'
    elif any(term in latest_action for term in ['passed', 'approved']):
        return 'Passed'
    elif any(term in latest_action for term in ['committee']):
        return 'In Committee'
    elif any(term in latest_action for term in ['failed', 'defeated', 'died']):
        return 'Failed'
    elif any(term in latest_action for term in ['vetoed']):
        return 'Vetoed'
    else:
        return 'Active'

def extract_year(date_string):
    """Extract year from date string"""
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00')).year
    except:
        return None

def process_legislation_data():
    """Main processing function"""
    
    bills = fetch_ai_legislation()
    
    if not bills:
        print("No bills found")
        return
    
    print(f"\nProcessing {len(bills)} bills...")
    
    processed_data = []
    seen_bills = set()
    filtered_out = 0
    
    for bill in bills:
        # Remove duplicates
        bill_key = f"{bill.get('jurisdiction', {}).get('name', '')}_{bill.get('identifier', '')}"
        if bill_key in seen_bills:
            continue
        seen_bills.add(bill_key)
        
        # Get bill details
        title = bill.get('title', '')
        abstract = ""
        if bill.get('abstracts'):
            abstract = bill['abstracts'][0].get('abstract', '') if bill['abstracts'] else ''
        
        # Filter for AI relevance
        if not is_ai_related(title, abstract):
            filtered_out += 1
            continue
        
        # Process bill data
        actions = bill.get('actions', [])
        year = extract_year(bill.get('created_at', ''))
        
        processed_bill = {
            'State': bill.get('jurisdiction', {}).get('name', ''),
            'Bill_ID': bill.get('identifier', ''),
            'Title': title,
            'Status': get_bill_status(actions),
            'Category': categorize_bill(title, abstract),
            'Year': year or 'Unknown',
            'Session': bill.get('session', ''),
            'Updated': bill.get('updated_at', ''),
            'URL': bill.get('sources', [{}])[0].get('url', '') if bill.get('sources') else '',
            'Last_Checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        processed_data.append(processed_bill)
    
    print(f"✓ Filtered out {filtered_out} non-AI bills")
    print(f"✓ Processing {len(processed_data)} AI-related bills")
    
    if not processed_data:
        print("No AI bills found after filtering")
        return
    
    # Sort by year (newest first), then state, then bill ID
    processed_data.sort(key=lambda x: (
        -x['Year'] if isinstance(x['Year'], int) else 0,
        x['State'],
        x['Bill_ID']
    ))
    
    # Create output directory
    os.makedirs('data', exist_ok=True)
    
    # Save main dataset
    fieldnames = ['State', 'Bill_ID', 'Title', 'Status', 'Category', 'Year', 'Session', 'Updated', 'URL', 'Last_Checked']
    
    with open('data/ai_legislation_bills.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"✓ Saved to data/ai_legislation_bills.csv")
    
    # Create state summary
    state_summary = {}
    for bill in processed_data:
        state = bill['State']
        if state not in state_summary:
            state_summary[state] = {
                'Total_Bills': 0,
                'Enacted': 0,
                'Active': 0,
                'Categories': set(),
                'Years': set()
            }
        
        state_summary[state]['Total_Bills'] += 1
        state_summary[state]['Categories'].add(bill['Category'])
        
        if isinstance(bill['Year'], int):
            state_summary[state]['Years'].add(str(bill['Year']))
        
        if bill['Status'] == 'Enacted':
            state_summary[state]['Enacted'] += 1
        elif bill['Status'] in ['Active', 'Passed', 'In Committee']:
            state_summary[state]['Active'] += 1
    
    # Generate summary data
    summary_data = []
    for state in sorted(state_summary.keys()):
        data = state_summary[state]
        
        # Determine framework status
        if data['Enacted'] >= 3:
            framework_status = 'Comprehensive'
        elif data['Enacted'] >= 1 or data['Total_Bills'] >= 3:
            framework_status = 'Some Activity'
        else:
            framework_status = 'Minimal'
        
        summary_data.append({
            'State': state,
            'Total_Bills': data['Total_Bills'],
            'Enacted': data['Enacted'],
            'Active_Pending': data['Active'],
            'Primary_Categories': '; '.join(sorted([cat for cat in data['Categories'] if cat != 'General AI'])[:3]),
            'Years_Active': '; '.join(sorted(data['Years'])),
            'Framework_Status': framework_status
        })
    
    # Sort by activity level
    summary_data.sort(key=lambda x: x['Total_Bills'], reverse=True)
    
    with open('data/ai_legislation_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        summary_fieldnames = ['State', 'Total_Bills', 'Enacted', 'Active_Pending', 'Primary_Categories', 'Years_Active', 'Framework_Status']
        writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
        writer.writeheader()
        writer.writerows(summary_data)
    
    print(f"✓ Saved summary to data/ai_legislation_summary.csv")
    
    print(f"\n=== SUCCESS ===")
    print(f"Created datasets with {len(processed_data)} AI bills from {len(state_summary)} states")
    
    # Show top states
    print(f"\nTop 5 most active states:")
    for i, state_data in enumerate(summary_data[:5], 1):
        print(f"  {i}. {state_data['State']}: {state_data['Total_Bills']} bills ({state_data['Enacted']} enacted)")

if __name__ == "__main__":
    process_legislation_data()
