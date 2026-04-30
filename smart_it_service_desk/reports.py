from datetime import datetime
from .logger import log_event


class ReportGenerator:
    def __init__(self, ticket_manager):
        self.ticket_manager = ticket_manager

    def _collect_stats(self):
        tickets = self.ticket_manager.tickets
        total = len(tickets)
        open_count = len([t for t in tickets if t.status != 'Closed'])
        closed_count = len([t for t in tickets if t.status == 'Closed'])
        high_priority = len([t for t in tickets if t.priority == 'P1'])
        sla_breaches = len(self.ticket_manager.sla_breaches())
        return {
            'total': total,
            'open': open_count,
            'closed': closed_count,
            'high_priority': high_priority,
            'sla_breaches': sla_breaches
        }

    def generate_daily_report(self):
        stats = self._collect_stats()
        today = datetime.now().date().isoformat()
        report = {
            'date': today,
            'summary': stats,
            'most_common_issue': self._most_common_issue(),
            'average_resolution_time': self._average_resolution_time(),
            'department_with_most_incidents': self._department_with_most_tickets(),
            'repeated_problems': [p.to_dict() for p in self.ticket_manager.get_problem_records() if p.occurrences >= 2]
        }
        self._write_report(f"daily_report_{today}.json", report)
        log_event('info', f"Daily report generated for {today}")
        return report

    def generate_monthly_report(self, year=None, month=None):
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        report_name = f"monthly_report_{year}_{month:02d}.json"
        report = {
            'period': f"{year}-{month:02d}",
            'summary': self._collect_stats(),
            'total_tickets': len(self.ticket_manager.tickets),
            'closed_tickets': len([t for t in self.ticket_manager.tickets if t.status == 'Closed']),
            'sla_breaches': len(self.ticket_manager.sla_breaches()),
            'problem_trends': [p.to_dict() for p in self.ticket_manager.get_problem_records()]
        }
        self._write_report(report_name, report)
        log_event('info', f"Monthly report generated for {year}-{month:02d}")
        return report

    def _most_common_issue(self):
        descriptions = [ticket.issue_description for ticket in self.ticket_manager.tickets]
        if not descriptions:
            return None
        frequency = {}
        for issue in descriptions:
            frequency[issue] = frequency.get(issue, 0) + 1
        return max(frequency, key=frequency.get)

    def _average_resolution_time(self):
        durations = []
        for ticket in self.ticket_manager.tickets:
            if ticket.resolved_date:
                created = datetime.fromisoformat(ticket.created_date)
                resolved = datetime.fromisoformat(ticket.resolved_date)
                durations.append((resolved - created).total_seconds())
        if not durations:
            return 'N/A'
        average_seconds = sum(durations) / len(durations)
        return f"{average_seconds / 3600:.2f} hours"

    def _department_with_most_tickets(self):
        department_counts = {}
        for ticket in self.ticket_manager.tickets:
            department_counts[ticket.department] = department_counts.get(ticket.department, 0) + 1
        if not department_counts:
            return None
        return max(department_counts, key=department_counts.get)

    def _write_report(self, filename, report_data):
        output_path = self.ticket_manager.ticket_file.replace('tickets.json', filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(report_data, f, indent=2)
        return output_path
