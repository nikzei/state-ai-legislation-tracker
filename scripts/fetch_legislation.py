import requests
import json
import os
import csv
from datetime import datetime, timedelta
import time

def fetch_ai_legislation_comprehensive():
    """Fetch AI-related bills from OpenStates API - comprehensive historical search"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        raise ValueError("OpenStates API key not found in environment variables")
    
    # Expanded search terms for comprehensive coverage
    search_terms = [
        "artificial intelligence",
        "automated decision",
        "machine learning",
        "algorithmic",
        "deepfake",
        "AI system",
        "neural network",
        "chatbot",
        "bot disclosure",
        "synthetic media",
        "computer-generated",
        "algorithm bias",
        "automated system"
    ]
    
    all_bills = []
    
    # Search without session restriction to get all historical data
    for term in search_terms:
        print(f"Searching for: {term}")
        
        # Start with basic search
        url = "https://v3.openstates.org/bills"
        params = {
            'q': term,
            'per_page': 100,  # Increased to get more results
            'sort': 'updated_at'
        }
        
        headers = {
            'X-API-KEY': api_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data:
                bills_found = len(data['results'])
                print(f"  Found {bills_found} bills for '{term}'")
                all_bills.extend(data['results'])
                
                # Check if there are more pages
                page = 1
                while 'next' in data and data['next'] and page < 5:  # Limit to 5 pages per term
                    page += 1
                    next_url = data['next']
                    
                    # Add API key to next URL
                    next_response = requests.get(next_url, headers=headers)
                    next_response.raise_for_status()
                    data = next_response.json()
                    
                    if 'results' in data:
                        additional_bills = len(data['results'])
                        print(f"  Found {additional_bills} more bills (page {page})")
                        all_bills.extend(data['results'])
                    
                    # Be nice to the API
                    time.sleep(0.5)
            else:
                print(f"  No results found for '{term}'")
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for term '{term}': {e}")
            continue
        
        # Be nice to the API between search terms
        time.sleep(1)
    
    print(f"Total bills collected: {len(all_bills)}")
    return all_bills

def is_ai_related(title, abstract=""):
    """Enhanced AI detection to filter out false positives"""
    text = (title + " " + abstract).lower()
    
    # Strong AI indicators
    ai_terms = [
        'artificial intelligence', 'ai system', 'ai technology', 'ai model',
        'machine learning', 'deep learning', 'neural network',
        'automated decision', 'algorithmic decision', 'algorithm bias',
        'chatbot', 'bot disclosure', 'conversational ai',
        'deepfake', 'synthetic media', 'computer-generated',
        'generative ai', 'large language model', 'llm'
    ]
    
    # Must contain at least one strong AI term
    if not any(term in text for term in ai_terms):
        return False
    
    # Exclude obvious false positives
    exclude_terms = [
        'agriculture', 'farming', 'crop', 'livestock', 'farm bill',
        'american indian', 'tribal', 'native american',
        'air quality', 'aviation', 'aircraft'
    ]
    
    if any(term in text for term in exclude_terms):
        return False
    
    return True

def categorize_bill(title, abstract=""):
    """Enhanced categorization with more specific categories"""
    text = (title + " " + abstract).lower()
    
    categories = []
    
    # Primary focus areas
    if any(term in text for term in ['healthcare', 'medical', 'health care', 'patient', 'clinical']):
        categories.append('Healthcare')
    if any(term in text for term in ['employment', 'hiring', 'workplace', 'job', 'worker', 'employee']):
        categories.append('Employment')
    if any(term in text for term in ['election', 'voting', 'campaign', 'political', 'deepfake']):
        categories.append('Elections')
    if any(term in text for term in ['privacy', 'data protection', 'personal information', 'consumer data']):
        categories.append('Privacy')
    if any(term in text for term in ['transparency', 'disclosure', 'watermark', 'explainable']):
        categories.append('Transparency')
    if any(term in text for term in ['government', 'agency', 'public sector', 'state use']):
        categories.append('Government Use')
    if any(term in text for term in ['chatbot', 'bot disclosure', 'conversational']):
        categories.append('Chatbots')
    if any(term in text for term in ['child', 'minor', 'exploitation', 'student', 'education']):
        categories.append('Child Protection/Education')
    if any(term in text for term in ['financial', 'banking', 'credit', 'lending', 'insurance']):
        categories.append('Financial Services')
    if any(term in text for term in ['criminal justice', 'law enforcement', 'policing', 'surveillance']):
        categories.append('Criminal Justice')
    if any(term in text for term in ['bias', 'discrimination', 'fairness', 'civil rights']):
        categories.append('Bias/Discrimination')
    if any(term in text for term in ['liability', 'safety', 'risk', 'harm']):
        categories.append('Safety/Liability')
    
    return '; '.join(categories) if categories else 'General AI'

def get_bill_status_category(actions):
    """Categorize bill status based on actions"""
    if not actions:
        return 'Introduced'
    
    latest_action = actions[0].get('description', '').lower()
    
    if any(term in latest_action for term in ['signed', 'enacted', 'effective', 'law']):
        return 'Enacted'
    elif any(term in latest_action for term in ['passed', 'approved']):
        return 'Passed'
    elif any(term in latest_action for term in ['committee', 'referred']):
        return 'In Committee'
    elif any(term in latest_action for term in ['failed', 'defeated', 'withdrawn']):
        return 'Failed/Withdrawn'
    elif any(term in latest_action for term in ['vetoed']):
        return 'Vetoed'
    else:
        return 'Active'

def process_legislation_data():
    """Process raw bill data into comprehensive tracker format"""
    
    print("Starting comprehensive AI legislation search...")
    bills = fetch_ai_legislation_comprehensive()
    
    if not bills:
        print("No bills found")
        return
    
    print("Filtering and processing bills...")
    processed_data = []
    seen_bills = set()  # To remove duplicates
    filtered_count = 0
    
    for bill in bills:
        # Create unique identifier
        bill_key = f"{bill.get('jurisdiction', {}).get('name', '')}_{bill.get('identifier', '')}"
        if bill_key in seen_bills:
            continue
        seen_bills.add(bill_key)
        
        # Enhanced AI filtering
        title = bill.get('title', '')
        abstract = ""
        if bill.get('abstracts'):
            abstract = bill['abstracts'][0].get('abstract', '') if bill['abstracts'] else ''
        
        if not is_ai_related(title, abstract):
            filtered_count += 1
            continue
        
        # Get status information
        actions = bill.get('actions', [])
        status_category = get_bill_status_category(actions)
        latest_action = actions[0].get('description', '') if actions else ''
        
        # Get session and year info
        session = bill.get('session', '')
        created_at = bill.get('created_at', '')
        year = ''
        if created_at:
            try:
                year = datetime.fromisoformat(created_at.replace('Z', '+00:00')).year
            except:
                pass
        
        processed_bill = {
            'State': bill.get('jurisdiction', {}).get('name', ''),
            'Bill_ID': bill.get('identifier', ''),
            'Title': title,
            'Status_Category': status_category,
            'Latest_Action': latest_action,
            'Category': categorize_bill(title, abstract),
            'Session': session,
            'Year': year,
            'Created': created_at,
            'Updated': bill.get('updated_at', ''),
            'URL': bill.get('sources', [{}])[0].get('url', '') if bill.get('sources') else '',
            'Abstract': abstract[:500] + '...' if len(abstract) > 500 else abstract,  # Truncate long abstracts
            'Last_Checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        processed_data.append(processed_bill)
    
    print(f"Filtered out {filtered_count} non-AI bills")
    print(f"Processing {len(processed_data)} AI-related bills")
    
    # Sort by Year (newest first), then State, then Bill_ID
    processed_data.sort(key=lambda x: (-x['Year'] if x['Year'] else 0, x['State'], x['Bill_ID']))
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save comprehensive bill data
    fieldnames = ['State', 'Bill_ID', 'Title', 'Status_Category', 'Latest_Action', 'Category', 
                  'Session', 'Year', 'Created', 'Updated', 'URL', 'Abstract', 'Last_Checked']
    
    with open('data/ai_legislation_comprehensive.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"Comprehensive data saved to data/ai_legislation_comprehensive.csv")
    
    # Create summary by state with status breakdown
    state_data = {}
    
    for bill in processed_data:
        state = bill['State']
        if state not in state_data:
            state_data[state] = {
                'Total_Bills': 0,
                'Enacted': 0,
                'Active': 0,
                'Failed': 0,
                'Categories': set(),
                'Years': set()
            }
        
        state_data[state]['Total_Bills'] += 1
        state_data[state]['Categories'].add(bill['Category'])
        if bill['Year']:
            state_data[state]['Years'].add(str(bill['Year']))
        
        # Count by status
        status = bill['Status_Category']
        if status == 'Enacted':
            state_data[state]['Enacted'] += 1
        elif status in ['Failed/Withdrawn', 'Vetoed']:
            state_data[state]['Failed'] += 1
        else:
            state_data[state]['Active'] += 1
    
    # Create state summary
    summary_data = []
    for state in sorted(state_data.keys()):
        data = state_data[state]
        summary_data.append({
            'State': state,
            'Total_Bills': data['Total_Bills'],
            'Enacted': data['Enacted'],
            'Active_Pending': data['Active'],
            'Failed_Vetoed': data['Failed'],
            'Categories': '; '.join(sorted(data['Categories'])),
            'Years_Active': '; '.join(sorted(data['Years'])),
            'Framework_Status': 'Comprehensive' if data['Enacted'] >= 3 else 'Some Activity' if data['Total_Bills'] >= 2 else 'Minimal'
        })
    
    # Sort by total bills (most active first)
    summary_data.sort(key=lambda x: x['Total_Bills'], reverse=True)
    
    with open('data/ai_legislation_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        summary_fieldnames = ['State', 'Total_Bills', 'Enacted', 'Active_Pending', 'Failed_Vetoed', 
                              'Categories', 'Years_Active', 'Framework_Status']
        writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
        writer.writeheader()
        writer.writerows(summary_data)
    
    print(f"State summary saved to data/ai_legislation_summary.csv")
    
    # Create year-over-year trend data
    year_data = {}
    for bill in processed_data:
        year = bill['Year']
        if year and year >= 2019:  # Focus on recent AI legislation era
            if year not in year_data:
                year_data[year] = {'Total': 0, 'Enacted': 0}
            year_data[year]['Total'] += 1
            if bill['Status_Category'] == 'Enacted':
                year_data[year]['Enacted'] += 1
    
    trend_data = []
    for year in sorted(year_data.keys()):
        trend_data.append({
            'Year': year,
            'Bills_Introduced': year_data[year]['Total'],
            'Bills_Enacted': year_data[year]['Enacted'],
            'Enactment_Rate': f"{(year_data[year]['Enacted'] / year_data[year]['Total'] * 100):.1f}%" if year_data[year]['Total'] > 0 else "0%"
        })
    
    with open('data/ai_legislation_trends.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Year', 'Bills_Introduced', 'Bills_Enacted', 'Enactment_Rate'])
        writer.writeheader()
        writer.writerows(trend_data)
    
    print(f"Trend analysis saved to data/ai_legislation_trends.csv")
    print(f"Total files created: 3 CSV files with comprehensive AI legislation data")

if __name__ == "__main__":
    process_legislation_data()
