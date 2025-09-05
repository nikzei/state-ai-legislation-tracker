import requests
import json
import os
import csv
from datetime import datetime
import time

def fetch_ai_legislation():
    """Minimal working version - copy exactly what worked in diagnostic"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        raise ValueError("OpenStates API key not found in environment variables")
    
    headers = {'X-API-KEY': api_key}
    all_bills = []
    
    print("=== MINIMAL WORKING VERSION ===\n")
    
    # Use EXACTLY the parameters that worked in diagnostic
    search_terms = ['AI']  # Start with just one term that worked
    
    for term in search_terms:
        print(f"Searching for: '{term}'")
        
        url = "https://v3.openstates.org/bills"
        params = {
            'q': term,
            'per_page': 3  # Use exact same number that worked in diagnostic
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            print(f"  Status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"  Error response: {response.text[:300]}")
                continue
                
            data = response.json()
            print(f"  Response keys: {list(data.keys())}")
            
            if 'results' in data and data['results']:
                bills_found = len(data['results'])
                print(f"  ✓ Found {bills_found} bills")
                
                # Print first bill for verification
                first_bill = data['results'][0]
                print(f"  Sample: {first_bill.get('identifier', 'No ID')} - {first_bill.get('title', 'No title')[:100]}")
                
                all_bills.extend(data['results'])
            else:
                print(f"  No results in response")
                
        except Exception as e:
            print(f"  Exception: {str(e)}")
            continue
    
    print(f"\nTotal bills collected: {len(all_bills)}")
    return all_bills

def simple_process():
    """Simple processing - just save what we get"""
    
    bills = fetch_ai_legislation()
    
    if not bills:
        print("No bills to process")
        return
    
    print(f"\nProcessing {len(bills)} bills...")
    
    # Create simple output
    processed_data = []
    
    for bill in bills:
        processed_bill = {
            'State': bill.get('jurisdiction', {}).get('name', 'Unknown'),
            'Bill_ID': bill.get('identifier', 'Unknown'),
            'Title': bill.get('title', 'No title'),
            'Session': bill.get('session', 'Unknown'),
            'Updated': bill.get('updated_at', 'Unknown'),
            'URL': bill.get('sources', [{}])[0].get('url', '') if bill.get('sources') else '',
            'Last_Checked': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        processed_data.append(processed_bill)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Save simple CSV
    fieldnames = ['State', 'Bill_ID', 'Title', 'Session', 'Updated', 'URL', 'Last_Checked']
    
    with open('data/ai_legislation_test.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"✓ Saved {len(processed_data)} bills to data/ai_legislation_test.csv")
    
    # Also create a summary
    states = {}
    for bill in processed_data:
        state = bill['State']
        states[state] = states.get(state, 0) + 1
    
    summary_data = [{'State': state, 'Bill_Count': count} for state, count in sorted(states.items())]
    
    with open('data/ai_legislation_test_summary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['State', 'Bill_Count'])
        writer.writeheader()
        writer.writerows(summary_data)
    
    print(f"✓ Saved summary to data/ai_legislation_test_summary.csv")
    print(f"\n=== SUCCESS ===")
    print(f"Found bills from states: {', '.join(states.keys())}")

# Also test the exact API call that worked in diagnostic
def verify_diagnostic():
    """Re-run the exact test that worked in diagnostic"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    headers = {'X-API-KEY': api_key}
    
    print("\n=== VERIFYING DIAGNOSTIC TEST ===")
    
    try:
        url = "https://v3.openstates.org/bills"
        params = {
            'q': 'AI',
            'per_page': 3
        }
        response = requests.get(url, params=params, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Results found: {len(data.get('results', []))}")
            if data.get('results'):
                bill = data['results'][0]
                print(f"Sample bill: {bill.get('identifier', 'Unknown')} - {bill.get('title', 'No title')[:100]}")
                return True
        else:
            print(f"Error response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # First verify the diagnostic still works
    if verify_diagnostic():
        print("✓ Diagnostic verification passed - proceeding with data collection")
        simple_process()
    else:
        print("✗ Diagnostic verification failed - API issue detected")
