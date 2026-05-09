# ServiceNow REST API integration (mocked)

from incident_tracker.utils.decorators import log_call, retry
from incident_tracker.config import MOCK_API, SERVICENOW_USER, SERVICENOW_PASS

@log_call
@retry(times=3)
def create_servicenow_ticket(incident):
    payload = {
        "short_description": incident.title,
        "description": incident.description,
        "urgency": 1 if incident.severity == 'critical' else 2 if incident.severity == 'high' else 3,
        "category": "IT",
        "assignment_group": incident.assigned_team
    }
    if MOCK_API:
        print("[MOCK ServiceNow] Payload:", payload)
        return f"MOCK-SNOW-{incident.id}"
    # Real API call would go here
    # ...
    return "REAL-SNOW-ID"
