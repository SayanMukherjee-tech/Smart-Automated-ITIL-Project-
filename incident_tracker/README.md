# IT Incident Auto-Triage & Tracker

A Python CLI tool that auto-classifies IT incidents and pushes them to three enterprise platforms (ServiceNow, Jira, Azure Boards) via mock REST APIs.

## Project Structure

```
incident_tracker/
├── main.py                 # CLI entry point
├── config.py               # API credentials and MOCK_API flag
├── models/
│   ├── __init__.py
│   ├── incident.py         # Incident base class and subclasses
│   └── report.py           # ReportGenerator (HTML/JSON output)
├── services/
│   ├── servicenow.py       # ServiceNow REST API integration
│   ├── jira.py             # Jira REST API integration
│   └── azure_boards.py     # Azure Boards REST API integration
├── utils/
│   ├── classifier.py       # Regex-based type and severity detection
│   ├── decorators.py       # @log_call and @retry decorators
│   └── helpers.py          # map/filter/reduce helper functions
├── data/
│   └── incidents.json      # Sample input — 12 incident records
└── output/
    ├── report.html         # Auto-generated HTML report
    └── report.json         # Auto-generated JSON summary
```

## Setup

1. Ensure Python 3.x is installed
2. No external dependencies required (uses standard library + mock mode)

## Running the Project

### Basic Run (Mock Mode)
```bash
python -m incident_tracker.main
```

### Filter by Severity
```bash
python -m incident_tracker.main --severity critical
python -m incident_tracker.main --severity high
python -m incident_tracker.main --severity medium
python -m incident_tracker.main --severity low
```

### Custom Input File
```bash
python -m incident_tracker.main --input path/to/incidents.json
```

## Configuration

Edit `config.py` to change settings:

```python
MOCK_API = True  # Set to False for real API calls

# Fill these with real credentials if MOCK_API = False
SERVICENOW_USER = ""
SERVICENOW_PASS = ""
JIRA_EMAIL = ""
JIRA_TOKEN = ""
AZURE_PAT = ""
```

## Features

- **Auto-classification**: Detects incident type (network/app/security) and severity (critical/high/medium/low) using regex
- **Mock Integrations**: Simulates ticket creation in ServiceNow, Jira, and Azure Boards
- **HTML Report**: Styled table with severity color-coding
- **JSON Export**: Machine-readable summary
- **Severity Filtering**: CLI flag to process only specific severity levels
- **Decorators**: @log_call and @retry for logging and resilience

## Output

- `output/report.html` - Styled HTML table with all incidents and ticket IDs
- `output/report.json` - JSON array with full incident details

## Sample Output

```
Loading incidents...
Loaded 12 incidents
Incidents by team: {'Database Team': 1, 'Security Team': 4, 'App Dev Team': 4, 'Network Team': 3}
Critical incidents: 3

Processing incidents and creating tickets...
Processing INC001: Database connection timeout on prod-db01
[MOCK ServiceNow] Payload: {...}
[MOCK Jira] Payload: {...}
[MOCK Azure Boards] Payload: {...}
...

Generating reports...
HTML report generated: incident_tracker/output/report.html
JSON report generated: incident_tracker/output/report.json

Done!
```