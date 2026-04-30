import csv
import os
from datetime import datetime, timedelta
from .utils import current_timestamp, generate_ticket_id, load_json, write_json, csv_backup, parse_datetime
from .logger import log_event, action_logger

PRIORITY_SLA = {
    'P1': 1,
    'P2': 4,
    'P3': 8,
    'P4': 24
}

ISSUE_PRIORITY = {
    'Server Down': 'P1',
    'Internet Down': 'P2',
    'Laptop Slow': 'P3',
    'Password Reset': 'P4',
    'Printer Failure': 'P2',
    'Application Crash': 'P1',
    'Disk Full': 'P1',
    'High CPU Usage': 'P1'
}

STATUS_OPTIONS = ['Open', 'In Progress', 'Resolved', 'Closed']


class TicketError(Exception):
    pass


class Ticket:
    def __init__(self, ticket_id, employee_name, department, issue_description, category, priority=None, status='Open', created_date=None):
        self.ticket_id = ticket_id
        self.employee_name = employee_name
        self.department = department
        self.issue_description = issue_description
        self.category = category
        self.priority = priority or self.issue_to_priority(issue_description)
        self.status = status
        self.created_date = created_date or current_timestamp()
        self.sla_deadline = self._compute_sla_deadline()
        self.resolved_date = None

    def issue_to_priority(self, issue_description):
        for key, value in ISSUE_PRIORITY.items():
            if key.lower() in issue_description.lower():
                return value
        return 'P4'

    def _compute_sla_deadline(self):
        hours = PRIORITY_SLA.get(self.priority, 24)
        return (parse_datetime(self.created_date) + timedelta(hours=hours)).isoformat()

    def update_status(self, new_status):
        if new_status not in STATUS_OPTIONS:
            raise TicketError(f"Invalid status: {new_status}")
        self.status = new_status
        if new_status == 'Closed':
            self.resolved_date = current_timestamp()
        log_event('info', f"Ticket {self.ticket_id} status updated to {new_status}")

    def is_sla_breached(self):
        if self.status != 'Closed':
            return parse_datetime(self.sla_deadline) < datetime.now()
        return False

    def to_dict(self):
        return {
            'ticket_id': self.ticket_id,
            'employee_name': self.employee_name,
            'department': self.department,
            'issue_description': self.issue_description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'created_date': self.created_date,
            'sla_deadline': self.sla_deadline,
            'resolved_date': self.resolved_date
        }

    @classmethod
    def from_dict(cls, data):
        ticket = cls(
            data['ticket_id'],
            data['employee_name'],
            data['department'],
            data['issue_description'],
            data['category'],
            data['priority'],
            data.get('status', 'Open'),
            data.get('created_date')
        )
        ticket.sla_deadline = data.get('sla_deadline', ticket.sla_deadline)
        ticket.resolved_date = data.get('resolved_date')
        return ticket

    def __str__(self):
        return f"{self.ticket_id} | {self.employee_name} | {self.department} | {self.priority} | {self.status}"

    def __repr__(self):
        return self.__str__()


class IncidentTicket(Ticket):
    def __init__(self, ticket_id, employee_name, department, issue_description, category, priority=None, status='Open', created_date=None, affected_service=None):
        super().__init__(ticket_id, employee_name, department, issue_description, category, priority, status, created_date)
        self.affected_service = affected_service or 'Core Service'

    def to_dict(self):
        data = super().to_dict()
        data['affected_service'] = self.affected_service
        return data


class ServiceRequest(Ticket):
    def __init__(self, ticket_id, employee_name, department, issue_description, category, priority=None, status='Open', created_date=None, request_type=None):
        super().__init__(ticket_id, employee_name, department, issue_description, category, priority, status, created_date)
        self.request_type = request_type or 'General Service Request'

    def to_dict(self):
        data = super().to_dict()
        data['request_type'] = self.request_type
        return data


class ProblemRecord:
    def __init__(self, problem_id, issue_description, occurrences=1, created_date=None, status='Open'):
        self.problem_id = problem_id
        self.issue_description = issue_description
        self.occurrences = occurrences
        self.created_date = created_date or current_timestamp()
        self.status = status

    def to_dict(self):
        return {
            'problem_id': self.problem_id,
            'issue_description': self.issue_description,
            'occurrences': self.occurrences,
            'created_date': self.created_date,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['problem_id'],
            data['issue_description'],
            data['occurrences'],
            data.get('created_date'),
            data.get('status', 'Open')
        )


class TicketIterator:
    def __init__(self, tickets, filter_status=None):
        self.tickets = [t for t in tickets if filter_status is None or t.status == filter_status]
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.tickets):
            raise StopIteration
        ticket = self.tickets[self.index]
        self.index += 1
        return ticket


class TicketManager:
    def __init__(self, ticket_file=None, problem_file=None, backup_file=None):
        base_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.ticket_file = ticket_file or os.path.join(base_dir, 'tickets.json')
        self.problem_file = problem_file or os.path.join(base_dir, 'problems.json')
        self.backup_file = backup_file or os.path.join(base_dir, 'backup.csv')
        self.tickets = self._load_tickets()
        self.problems = self._load_problems()

    def _load_tickets(self):
        data = load_json(self.ticket_file, default=[])
        return [Ticket.from_dict(item) for item in data]

    def _save_tickets(self):
        write_json(self.ticket_file, [t.to_dict() for t in self.tickets])

    def _load_problems(self):
        data = load_json(self.problem_file, default=[])
        return [ProblemRecord.from_dict(item) for item in data]

    def _save_problems(self):
        write_json(self.problem_file, [p.to_dict() for p in self.problems])

    @action_logger
    def create_ticket(self, employee_name, department, issue_description, category, ticket_type='Incident'):
        if not employee_name or not department or not issue_description or not category:
            log_event('error', 'Attempted to create ticket with empty required values')
            raise TicketError('Employee name, department, issue description, and category are required.')
        existing_ids = [ticket.ticket_id for ticket in self.tickets]
        ticket_id = generate_ticket_id(existing_ids, prefix='TKT')
        if ticket_type == 'Service Request':
            ticket = ServiceRequest(ticket_id, employee_name, department, issue_description, category)
        else:
            ticket = IncidentTicket(ticket_id, employee_name, department, issue_description, category)
        self.tickets.append(ticket)
        self._save_tickets()
        log_event('info', f'Ticket created: {ticket.ticket_id}')
        return ticket

    def view_all(self):
        return sorted(self.tickets, key=lambda item: (item.priority, item.status, item.created_date))

    def search_by_id(self, ticket_id):
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        raise TicketError(f"Ticket {ticket_id} not found.")

    @action_logger
    def update_ticket(self, ticket_id, status=None, priority=None):
        ticket = self.search_by_id(ticket_id)
        if priority:
            ticket.priority = priority
            ticket.sla_deadline = ticket._compute_sla_deadline()
        if status:
            ticket.update_status(status)
        self._save_tickets()
        return ticket

    @action_logger
    def close_ticket(self, ticket_id):
        ticket = self.search_by_id(ticket_id)
        ticket.update_status('Closed')
        self._save_tickets()
        return ticket

    @action_logger
    def delete_ticket(self, ticket_id):
        ticket = self.search_by_id(ticket_id)
        self.tickets = [t for t in self.tickets if t.ticket_id != ticket_id]
        self._save_tickets()
        log_event('warning', f'Ticket deleted: {ticket_id}')
        return ticket

    @action_logger
    def backup_to_csv(self):
        header = ['ticket_id', 'employee_name', 'department', 'issue_description', 'category', 'priority', 'status', 'created_date', 'sla_deadline', 'resolved_date']
        rows = [[
            ticket.ticket_id,
            ticket.employee_name,
            ticket.department,
            ticket.issue_description,
            ticket.category,
            ticket.priority,
            ticket.status,
            ticket.created_date,
            ticket.sla_deadline,
            ticket.resolved_date or ''
        ] for ticket in self.tickets]
        csv_backup(self.backup_file, header, rows)
        return self.backup_file

    def pending_tickets(self):
        return [ticket for ticket in self.tickets if ticket.status != 'Closed']

    def sla_breaches(self):
        return [ticket for ticket in self.pending_tickets() if ticket.is_sla_breached()]

    def record_problem(self, issue_description):
        matches = [p for p in self.problems if p.issue_description.lower() == issue_description.lower()]
        if matches:
            problem = matches[0]
            problem.occurrences += 1
        else:
            problem_id = f"PRB-{len(self.problems) + 1:03d}"
            problem = ProblemRecord(problem_id, issue_description, occurrences=1)
            self.problems.append(problem)
        if problem.occurrences >= 5 and problem.status == 'Open':
            log_event('warning', f"Problem record created for repeated issue: {problem.issue_description}")
        self._save_problems()
        return problem

    def get_problem_records(self):
        return sorted(self.problems, key=lambda item: item.occurrences, reverse=True)

    def get_statistics(self):
        stats = {
            'total': len(self.tickets),
            'open': len([t for t in self.tickets if t.status != 'Closed']),
            'closed': len([t for t in self.tickets if t.status == 'Closed']),
            'high_priority': len([t for t in self.tickets if t.priority == 'P1'])
        }
        return stats
