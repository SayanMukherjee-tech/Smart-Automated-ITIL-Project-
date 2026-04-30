from .tickets import ProblemRecord
from .logger import log_event


class ChangeRecord:
    def __init__(self, change_id, description, requested_by, status='Pending', created_date=None):
        self.change_id = change_id
        self.description = description
        self.requested_by = requested_by
        self.status = status
        self.created_date = created_date

    def to_dict(self):
        return {
            'change_id': self.change_id,
            'description': self.description,
            'requested_by': self.requested_by,
            'status': self.status,
            'created_date': self.created_date
        }


class ITILManager:
    def __init__(self, ticket_manager):
        self.ticket_manager = ticket_manager
        self.change_records = []

    def incident_management(self):
        open_incidents = [t for t in self.ticket_manager.tickets if isinstance(t, ProblemRecord) is False]
        log_event('info', f"Incident management checked {len(open_incidents)} tickets")
        return open_incidents

    def service_request_management(self):
        requests = [t for t in self.ticket_manager.tickets if t.category.lower() == 'service request']
        log_event('info', f"Service request management found {len(requests)} records")
        return requests

    def problem_management(self):
        problems = self.ticket_manager.get_problem_records()
        log_event('info', f"Problem management found {len(problems)} problem records")
        return problems

    def change_management(self, description, requested_by):
        change_id = f"CHG-{len(self.change_records) + 1:03d}"
        record = ChangeRecord(change_id, description, requested_by, status='Pending', created_date=None)
        self.change_records.append(record)
        log_event('info', f"Change request created: {change_id}")
        return record

    def sla_monitoring(self):
        breaches = self.ticket_manager.sla_breaches()
        if breaches:
            log_event('warning', f"SLA breach detected for {len(breaches)} tickets")
        return breaches
