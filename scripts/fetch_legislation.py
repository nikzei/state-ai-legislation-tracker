import requests
import json
import os
from datetime import datetime

def test_openstates_api():
    """Test different OpenStates API endpoints to find what works"""
    
    api_key = os.environ.get('OPENSTATES_API_KEY')
    if not api_key:
        print("ERROR: No API key found")
        return
    
    print("=== OPENSTATES API DIAGNOSTIC ===\n")
    print(f"API Key present: {bool(api_key)}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    
    headers = {'X-API-KEY': api_key}
    
    # Test 1: Basic API connection
    print("\n1. Testing basic API connection...")
    try:
        url = "https://v3.openstates.org/"
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Try the bills endpoint without parameters
    print("\n2. Testing bills endpoint (no parameters)...")
    try:
        url = "https://v3.openstates.org/bills"
        response = requests.get(url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Results found: {len(data.get('results', []))}")
            if data.get('results'):
                print(f"   First bill state: {data['results'][0].get('jurisdiction', {}).get('name', 'Unknown')}")
        else:
            print(f"   Error response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Try with minimal parameters
    print("\n3. Testing with minimal parameters...")
    try:
        url = "https://v3.openstates.org/bills"
        params = {'per_page': 5}
        response = requests.get(url, params=params, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Results found: {len(data.get('results', []))}")
        else:
            print(f"   Error response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Try with state filter instead of search
    print("\n4. Testing with state filter...")
    try:
        url = "https://v3.openstates.org/bills"
        params = {
            'jurisdiction': 'California',
            'per_page': 5
        }
        response = requests.get(url, params=params, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Results found: {len(data.get('results', []))}")
        else:
            print(f"   Error response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Try a very simple search
    print("\n5. Testing simple search...")
    try:
        url = "https://v3.openstates.org/bills"
        params = {
            'q': 'AI',
            'per_page': 3
        }
        response = requests.get(url, params=params, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Results found: {len(data.get('results', []))}")
            if data.get('results'):
                bill = data['results'][0]
                print(f"   Sample bill: {bill.get('identifier', 'Unknown')} - {bill.get('title', 'No title')[:100]}")
        else:
            print(f"   Error response: {response.text[:500]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== DIAGNOSTIC COMPLETE ===")

# Alternative: Try different API approach entirely
def test_alternative_approach():
    """Test a completely different approach to getting legislation data"""
    
    print("\n=== ALTERNATIVE APPROACH TEST ===")
    
    # Maybe we need to use a different base URL or approach
    api_key = os.environ.get('OPENSTATES_API_KEY')
    headers = {'X-API-KEY': api_key}
    
    # Test different potential endpoints
    test_urls = [
        "https://openstates.org/api/v1/bills/",
        "https://v3.openstates.org/bills/",
        "https://api.openstates.org/v3/bills/",
        "https://v3.openstates.org/bills"
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        try:
            response = requests.get(url, headers=headers, params={'per_page': 1})
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   SUCCESS! This URL works")
                data = response.json()
                print(f"   Data keys: {list(data.keys())}")
                break
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_openstates_api()
    test_alternative_approach()
