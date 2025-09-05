name: Update AI Legislation Data

on:
  schedule:
    # Run twice per week: Monday and Thursday at 9 AM UTC
    - cron: '0 9 * * 1,4'
  workflow_dispatch:  # Allows manual triggering

jobs:
  update-data:
    runs-on: ubuntu-latest
    timeout-minutes: 15  # Increased timeout for comprehensive search
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Fetch and process comprehensive legislation data
      env:
        OPENSTATES_API_KEY: ${{ secrets.OPENSTATES_API_KEY }}
      run: |
        python scripts/fetch_legislation.py
        
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/ || true
        if [ -n "$(git status --porcelain)" ]; then
          git commit -m "Auto-update: Comprehensive AI legislation data $(date '+%Y-%m-%d %H:%M:%S')"
          git push
        else
          echo "No changes to commit"
        fi
