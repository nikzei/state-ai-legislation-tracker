import requests
import json
import os
import csv
from datetime import datetime
import time

def fetch_ai_legislation_comprehensive():
    """Comprehensive AI legislation fetcher using small page sizes that work"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        raise ValueError("OpenStates API key not found in environment variables")
    
    headers = {'X-API-KEY': api_key}
    all_bills = []
    
    print("=== COMPREHENSIVE AI LEGISLATION TRACKER ===\n")
    
    # Multiple search terms, smaller page sizes
    search_terms = [
        'AI',
        'artificial intelligence', 
        'deepfake',
        'chatbot',
        'algorithmic',
        'automated decision',
        'machine learning',
        'algorithm bias',
        'synthetic media',
        'bot disclosure'
    ]
    
    for term in search_terms:
        print(f"Searching for: '{term}'")
        
        url = "https://v3.openstates.org/bills"
        params = {
            'q': term,
            'per_page': 20  # Use smaller page size that works
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                print(f"  ✗ Status {response.status_code}: {response.text[:200]}")
                continue
                
            data = response.json()
            
            if 'results' in data and data['results']:
                bills_found = len(data['results'])
                print(f"  ✓ Found {bills_found} bills")
                all_bills.extend(data['results'])
                
                # Get additional pages if available
                page = 1
                while 'pagination' in data and data['pagination'].get('next_url') and page < 5:
                    page += 1
                    next_url = data['pagination']['next_url']
                    
                    print(f"    Getting page {page}...")
                    next_response = requests.get(next_url, headers=headers)
                    
                    if next_response.status_code == 200:
                        data = next_response.json()
                        if 'results' in data and data['results']:
                            additional_bills = len(data['results'])
                            print(f"    ✓ Found {additional_bills} more bills")
                            all_bills.extend(data['results'])
                        else:
                            break
                    else:
                        print(f"    ✗ Page {page} failed: {next_response.status_code}")
                        break
                    
                    time.sleep(2)  # Pause between pages
            else:
                print(f"  No results for '{term}'")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            continue
        
        # Pause between search terms to be nice to API
        time.sleep(3)
    
    print(f"\n=== COLLECTION SUMMARY ===")
    print(f"Total bills collected: {len(all_bills)}")
    
    # Remove duplicates
    seen_bills = set()
    unique_bills = []
    
    for bill in all_bills:
        bill_key = f"{bill.get('jurisdiction', {}).get('name', '')}_{bill.get('identifier', '')}"
        if bill_key not in seen_bills:
            seen_bills.add(bill_key)
            unique_bills.append(bill)
    
    print(f"Unique bills after deduplication: {len(unique_bills)}")
    return unique_bills

def is_ai_related(title, abstract=""):
    """Enhanced AI filtering"""
    text = (title + " " + abstract).lower()
    
    # Strong AI indicators - must have at least one
    ai_terms = [
        'artificial intelligence', 'ai ', ' ai', 'a.i.',
        'machine learning', 'deep learning', 'neural network',
        'automated decision', 'algorithmic decision', 'algorithm',
        'chatbot', 'bot ', 'deepfake', 'synthetic media',
        'generative ai', 'large language model', 'llm',
        'computer-generated', 'ai-generated'
    ]
    
    has_ai_term = any(term in text for term in ai_terms)
    
    # Exclude obvious false positives
    exclude_terms = [
        'agriculture', 'farming', 'crop', 'livestock',
        'american indian', 'tribal', 'native american',
        'air quality', 'aviation', 'aircraft', 'airport',
        'artificial insemination', 'aid to families',
        'academic improvement', 'adequate improvement'
    ]
    
    has_exclude = any(term in text for term in exclude_terms)
    
    return has_ai_term and not has_exclude

def categorize_bill(title, abstract=""):
    """Categorize AI bills by focus area"""
    text = (title + " " + abstract).lower()
    
    categories = []
    
    # Primary categories
    if any(term in text for term in ['health', 'medical', 'patient', 'clinical', 'healthcare']):
        categories.append('Healthcare')
    if any(term in text for term in ['employ', 'hiring', 'workplace', 'job', 'worker', 'labor']):
        categories.append('Employment')
    if any(term in text for term in ['election', 'voting', 'campaign', 'political', 'deepfake']):
        categories.append('Elections')
    if any(term in text for term in ['privacy', 'data protection', 'personal information', 'consumer data']):
        categories.append('Privacy')
    if any(term in text for term in ['transparency', 'disclosure', 'explainable', 'audit', 'watermark']):
        categories.append('Transparency')
    if any(term in text for term in ['government', 'agency', 'public', 'state agency']):
        categories.append('Government Use')
    if any(term in text for term in ['chatbot', 'bot disclosure', 'conversational ai']):
        categories.append('Chatbots')
    if any(term in text for term in ['child', 'minor', 'student', 'education', 'school', 'exploitation']):
        categories.append('Education/Child Protection')
    if any(term in text for term in ['bias', 'discrimination', 'fairness', 'civil rights', 'equal']):
        categories.append('Bias/Discrimination')
    if any(term in text for term in ['financial', 'banking', 'credit', 'lending', 'insurance']):
        categories.append('Financial Services')
    if any(term in text for term in ['criminal', 'law enforcement', 'police', 'surveillance', 'justice']):
        categories.append('Criminal Justice')
    if any(term in text for term in ['liability', 'safety', 'risk', 'harm', 'security']):
        categories.append('Safety/Liability')
    
    return '; '.join(categories) if categories else 'General AI'

def get_bill_status(actions):
    """Determine bill status from actions"""
    if not actions:
        return 'Introduced'
    
    # Look at most recent action
    latest_action = actions[0].get('description', '').lower()
    
    if any(term in latest_action for term in ['signed', 'enacted', 'effective', 'chaptered', 'became law']):
        return 'Enacted'
    elif any(term in latest_action for term in ['passed', 'approved']):
        return 'Passed'
    elif any(term in latest_action for term in ['committee', 'referred', 'assigned']):
        return 'In Committee'
    elif any(term in latest_action for term in ['failed', 'defeated', 'died', 'withdrawn']):
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
        try:
            # Try alternative date format
            return int(date_string[:4]) if date_string and len(date_string) >= 4 else None
        except:
            return None

def process_comprehensive_data():
    """Main processing function"""
    
    bills = fetch_ai_legislation_comprehensive()
    
    if not bills:
        print("No bills to process")
        return
    
    print(f"\nProcessing {len(bills)} bills for AI relevance...")
    
    processed_data = []
    filtered_out = 0
    
    for bill in bills:
        title = bill.get('title', '')
        abstract = ""
        
        # Get abstract if available
        if bill.get('abstracts'):
            abstract = bill['abstracts'][0].get('abstract', '') if bill['abstracts'] else ''
        
        # Filter for AI relevance
        if not is_ai_related(title, abstract):
            filtered_out += 1
            continue
        
        # Extract bill information
        actions = bill.get('actions', [])
        year = extract_year(bill.get('created_at', ''))
        
        processed_bill = {
            'State': bill.get('jurisdiction', {}).get('name', ''),
            'Bill_ID': bill.get('identifier', ''),
            'Title': title,
            'Status': get_bill_status(actions),
            'Category': categorize_bill(title, abstract),
            'Year': year if year else 'Unknown',
            'Session': bill.get('session', ''),
            'Updated': bill.get('updated_at', ''),
            'URL': bill.get('sources', [{}])[0].get('url', '') if bill.get('sources') else '',
            'Last_Checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        processed_data.append(processed_bill)
    
    print(f"✓ Filtered out {filtered_out} non-AI bills")
    print(f"✓ Processing {len(processed_data)} confirmed AI bills")
    
    if not processed_data:
        print("No confirmed AI bills found")
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
    category_counts = {}
    
    for bill in processed_data:
        state = bill['State']
        
        # Count by state
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
        
        # Count by status
        if bill['Status'] == 'Enacted':
            state_summary[state]['Enacted'] += 1
        elif bill['Status'] in ['Active', 'Passed', 'In Committee']:
            state_summary[state]['Active'] += 1
        
        # Count categories across all bills
        if bill['Category']:
            for category in bill['Category'].split('; '):
                category_counts[category] = category_counts.get(category, 0) + 1
    
    # Create summary data
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
    
    # Sort by total activity
    summary_data.sort(key=lambda x: x['Total_Bills'], reverse=True)
    
    with open('data/ai_legislation_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        summary_fieldnames = ['State', 'Total_Bills', 'Enacted', 'Active_Pending', 'Primary_Categories', 'Years_Active', 'Framework_Status']
        writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
        writer.writeheader()
        writer.writerows(summary_data)
    
    print(f"✓ Saved summary to data/ai_legislation_summary.csv")
    
    print(f"\n=== COMPREHENSIVE SUCCESS ===")
    print(f"Created datasets with {len(processed_data)} AI bills from {len(state_summary)} states")
    
    # Show top results
    print(f"\nTop 5 most active states:")
    for i, state_data in enumerate(summary_data[:5], 1):
        print(f"  {i}. {state_data['State']}: {state_data['Total_Bills']} bills ({state_data['Enacted']} enacted)")
    
    print(f"\nTop categories:")
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
    for category, count in sorted_categories[:5]:
        print(f"  {category}: {count} bills")

if __name__ == "__main__":
    process_comprehensive_data()
