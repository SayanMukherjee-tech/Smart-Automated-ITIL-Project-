# Smart IT Service Desk

A complete Python backend automation project for ITIL incident, service request, problem, and SLA management.

## Project Overview

This repository contains a CLI-based IT Service Desk system that automates ticket creation, monitoring alerts, SLA tracking, reporting, logging, and backup.

## Structure

```
smart_it_service_desk/
│── __init__.py
│── main.py
│── tickets.py
│── monitor.py
│── reports.py
│── itil.py
│── utils.py
│── logger.py
│── README.md
│── requirements.txt
│── data/
│   ├── tickets.json
│   ├── problems.json
│   ├── backup.csv
│   ├── logs.txt
│   └── daily_report_2026-04-30.json
│── tests/
    ├── __init__.py
    └── test_ticket_system.py
.github/
└── workflows/
    └── python-app.yml
```

## Setup

```bash
cd "c:\Users\asus\OneDrive\Desktop\MINI PROJECT 3"
pip install -r smart_it_service_desk/requirements.txt
```

## Usage

Run the CLI from the repository root:

```bash
python -m smart_it_service_desk.main create --name "Anna Lee" --department "IT" --issue "Laptop Slow" --category "Service Request" --type "Service Request"
python -m smart_it_service_desk.main list
python -m smart_it_service_desk.main search TKT-001
python -m smart_it_service_desk.main update TKT-001 --status "In Progress"
python -m smart_it_service_desk.main close TKT-001
python -m smart_it_service_desk.main delete TKT-002
python -m smart_it_service_desk.main backup
python -m smart_it_service_desk.main monitor
python -m smart_it_service_desk.main daily-report
python -m smart_it_service_desk.main monthly-report
python -m smart_it_service_desk.main problems
python -m smart_it_service_desk.main sla-breaches
```

## Testing

```bash
python -m unittest discover -s smart_it_service_desk/tests
```

## GitHub Deployment

Push this repository to GitHub and the included workflow will run tests automatically on every push.

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Notes

- The CLI is the primary interface for the project.
- Monitoring alerts automatically create high-priority tickets.
- Reports are generated in JSON format under `smart_it_service_desk/data/`.
