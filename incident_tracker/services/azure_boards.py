# Azure Boards REST API integration (mocked)

from incident_tracker.utils.decorators import log_call, retry
from incident_tracker.config import MOCK_API, AZURE_PAT

@log_call
@retry(times=3)
def create_azure_work_item(incident):
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": incident.title},
        {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": incident.severity.capitalize()},
        {"op": "add", "path": "/fields/System.AssignedTo", "value": incident.assigned_team}
    ]
    if MOCK_API:
        print("[MOCK Azure Boards] Payload:", payload)
        return f"MOCK-AZURE-{incident.id}"
    # Real API call would go here
    # ...
    return "REAL-AZURE-ID"
