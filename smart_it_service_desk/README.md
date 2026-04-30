# Smart IT Service Desk

A Python backend automation system for ITIL ticket management, monitoring, SLA tracking, reporting, and problem management.

## Project Structure

```
smart_it_service_desk/
│── main.py
│── tickets.py
│── monitor.py
│── reports.py
│── itil.py
│── utils.py
│── logger.py
│── data/
│   ├── tickets.json
│   ├── logs.txt
│   ├── backup.csv
│   └── problems.json
│── requirements.txt
│── README.md
│── tests/
    ├── __init__.py
    └── test_ticket_system.py
```

## Setup

1. Install Python 3.10+.
2. Install the required package:

```bash
pip install -r smart_it_service_desk/requirements.txt
```

## Running the Project

Run the CLI from the workspace root:

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

## Features

- Ticket creation, search, update, close, delete
- SLA tracking and breach detection
- Automated monitor alerts for CPU, memory, disk, and network usage
- JSON storage for tickets and problem records
- CSV backup export
- Daily and monthly reports
- ITIL incident, service request, problem, and change management
- Logging with INFO, WARNING, ERROR, CRITICAL levels

## Data Files

- `data/tickets.json` stores active tickets.
- `data/problems.json` stores repeated problem records.
- `data/backup.csv` stores CSV backup output.
- `data/logs.txt` stores log history.

## Testing

Run tests with:

```bash
python -m unittest discover -s smart_it_service_desk/tests
```
