import argparse

from .tickets import TicketManager, TicketError
from .monitor import Monitor
from .reports import ReportGenerator
from .itil import ITILManager
from .utils import safe_input


def print_ticket(ticket):
    if not ticket:
        return
    print('-' * 80)
    for key, value in ticket.to_dict().items():
        print(f"{key}: {value}")
    print('-' * 80)


def main():
    parser = argparse.ArgumentParser(description='Smart IT Service Desk CLI')
    subparsers = parser.add_subparsers(dest='command')

    create_parser = subparsers.add_parser('create', help='Create a new ticket')
    create_parser.add_argument('--name', help='Employee name')
    create_parser.add_argument('--department', help='Department')
    create_parser.add_argument('--issue', help='Issue description')
    create_parser.add_argument('--category', help='Category')
    create_parser.add_argument('--type', choices=['Incident', 'Service Request'], default='Incident', help='Ticket type')

    subparsers.add_parser('list', help='List all tickets')
    search_parser = subparsers.add_parser('search', help='Search ticket by ID')
    search_parser.add_argument('ticket_id', help='Ticket ID')

    update_parser = subparsers.add_parser('update', help='Update ticket status')
    update_parser.add_argument('ticket_id', help='Ticket ID')
    update_parser.add_argument('--status', choices=['Open', 'In Progress', 'Resolved', 'Closed'], required=True)

    close_parser = subparsers.add_parser('close', help='Close a ticket')
    close_parser.add_argument('ticket_id', help='Ticket ID')

    delete_parser = subparsers.add_parser('delete', help='Delete a ticket')
    delete_parser.add_argument('ticket_id', help='Ticket ID')

    subparsers.add_parser('backup', help='Backup tickets to CSV')
    subparsers.add_parser('monitor', help='Run system monitor scan')
    subparsers.add_parser('daily-report', help='Generate daily report')
    subparsers.add_parser('monthly-report', help='Generate monthly report')
    subparsers.add_parser('problems', help='Show problem records')
    subparsers.add_parser('sla-breaches', help='Show SLA breaches')

    args = parser.parse_args()
    manager = TicketManager()
    monitor = Monitor(manager)
    report_gen = ReportGenerator(manager)
    itil = ITILManager(manager)

    if args.command == 'create':
        name = args.name or safe_input('Employee Name: ')
        department = args.department or safe_input('Department: ')
        issue = args.issue or safe_input('Issue Description: ')
        category = args.category or safe_input('Category: ')
        ticket_type = args.type
        ticket = manager.create_ticket(name, department, issue, category, ticket_type)
        print('Ticket created:')
        print_ticket(ticket)

    elif args.command == 'list':
        for ticket in manager.view_all():
            print(ticket)

    elif args.command == 'search':
        try:
            ticket = manager.search_by_id(args.ticket_id)
            print_ticket(ticket)
        except TicketError as err:
            print(err)

    elif args.command == 'update':
        try:
            ticket = manager.update_ticket(args.ticket_id, status=args.status)
            print('Updated ticket:')
            print_ticket(ticket)
        except TicketError as err:
            print(err)

    elif args.command == 'close':
        try:
            ticket = manager.close_ticket(args.ticket_id)
            print('Closed ticket:')
            print_ticket(ticket)
        except TicketError as err:
            print(err)

    elif args.command == 'delete':
        try:
            ticket = manager.delete_ticket(args.ticket_id)
            print(f'Deleted ticket {ticket.ticket_id}')
        except TicketError as err:
            print(err)

    elif args.command == 'backup':
        backup_file = manager.backup_to_csv()
        print(f'Backup written to {backup_file}')

    elif args.command == 'monitor':
        metrics = monitor.scan_resources()
        print('Monitor scan completed.')
        print(metrics)

    elif args.command == 'daily-report':
        report = report_gen.generate_daily_report()
        print('Daily report generated:')
        print(report)

    elif args.command == 'monthly-report':
        report = report_gen.generate_monthly_report()
        print('Monthly report generated:')
        print(report)

    elif args.command == 'problems':
        problems = itil.problem_management()
        for problem in problems:
            print(problem.to_dict())

    elif args.command == 'sla-breaches':
        breaches = itil.sla_monitoring()
        for ticket in breaches:
            print(ticket)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
