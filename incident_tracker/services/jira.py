# Jira REST API integration (mocked)

from incident_tracker.utils.decorators import log_call, retry
from incident_tracker.config import MOCK_API, JIRA_EMAIL, JIRA_TOKEN

@log_call
@retry(times=3)
def create_jira_issue(incident):
    payload = {
        "fields": {
            "summary": incident.title,
            "description": incident.description,
            "issuetype": {"name": "Bug"},
            "priority": {"name": incident.severity.capitalize()},
            "project": {"key": "DEMO"},
            "labels": [incident.assigned_team]
        }
    }
    if MOCK_API:
        print("[MOCK Jira] Payload:", payload)
        return f"MOCK-JIRA-{incident.id}"
    # Real API call would go here
    # ...
    return "REAL-JIRA-ID"
