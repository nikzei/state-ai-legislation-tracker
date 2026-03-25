# AI Legislation Tracker

Automated tracking of AI-related legislation across U.S. states, powered by the [OpenStates API](https://openstates.org/api/). Data is fetched and updated automatically twice per week.

-----

## 📋 Overview

This repository maintains a continuously updated dataset of state-level AI legislation. A GitHub Actions workflow runs on a schedule to pull the latest bill data, process it, and commit any changes directly to this repo — no manual intervention required.

-----

## 📁 Repository Structure

```
├── .github/
│   └── workflows/
│       └── update_legislation.yml   # Automated data update workflow
├── data/                            # Output: processed legislation data
├── scripts/
│   └── fetch_legislation.py         # Core data fetching & processing script
├── requirements.txt                 # Python dependencies
└── README.md
```

-----

## ⚙️ How It Works

1. **Scheduled Trigger** — The workflow runs automatically every **Monday and Thursday at 9 AM UTC**. It can also be triggered manually from the GitHub Actions tab.
1. **Data Fetch** — `fetch_legislation.py` calls the OpenStates API to retrieve current AI-related bills from state legislatures.
1. **Processing** — The script processes and structures the raw data into the `/data` directory.
1. **Auto-Commit** — If new or changed data is detected, the workflow commits and pushes the update with a timestamped message. If nothing has changed, no commit is made.

-----

## 🚀 Setup

### Prerequisites

- Python 3.11+
- An [OpenStates API key](https://openstates.org/api/register/)

### Local Development

1. **Clone the repository**
   
   ```bash
   git clone https://github.com/your-org/your-repo.git
   cd your-repo
   ```
1. **Install dependencies**
   
   ```bash
   pip install -r requirements.txt
   ```
1. **Set your API key**
   
   ```bash
   export OPENSTATES_API_KEY=your_api_key_here
   ```
1. **Run the fetch script**
   
   ```bash
   python scripts/fetch_legislation.py
   ```

### GitHub Actions Setup

To enable the automated workflow in your own fork:

1. Go to **Settings → Secrets and variables → Actions**
1. Add a new repository secret:
- **Name:** `OPENSTATES_API_KEY`
- **Value:** Your OpenStates API key

The workflow will then run automatically on its schedule.

-----

## 🔄 Workflow Schedule

|Trigger  |Schedule                           |
|---------|-----------------------------------|
|Automatic|Mondays at 9:00 AM UTC             |
|Automatic|Thursdays at 9:00 AM UTC           |
|Manual   |Via GitHub Actions → “Run workflow”|

-----

## 📊 Data

Processed legislation data is stored in the `/data` directory and updated automatically. Each update is timestamped in the commit message (e.g., `Auto-update: Comprehensive AI legislation data 2026-03-24 09:00:00`).

-----

## 🛠️ Contributing

Contributions are welcome! To suggest changes to the data pipeline or add new features:

1. Fork the repository
1. Create a feature branch (`git checkout -b feature/your-feature`)
1. Commit your changes
1. Open a pull request

-----

## 📄 License

This project is open source. See <LICENSE> for details.

-----

## 🙏 Acknowledgements

- Legislation data provided by [OpenStates](https://openstates.org/)
- Automated via [GitHub Actions](https://github.com/features/actions)
