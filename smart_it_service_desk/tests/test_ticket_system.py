import os
import tempfile
import unittest

from smart_it_service_desk.tickets import TicketManager, TicketError
from smart_it_service_desk.monitor import Monitor


class TicketSystemTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.ticket_file = os.path.join(self.tempdir.name, 'tickets.json')
        self.problem_file = os.path.join(self.tempdir.name, 'problems.json')
        self.backup_file = os.path.join(self.tempdir.name, 'backup.csv')
        self.manager = TicketManager(ticket_file=self.ticket_file, problem_file=self.problem_file, backup_file=self.backup_file)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_ticket_creation(self):
        ticket = self.manager.create_ticket('Test User', 'IT', 'Server Down', 'Incident')
        self.assertEqual(ticket.priority, 'P1')
        self.assertEqual(ticket.status, 'Open')
        self.assertTrue(os.path.exists(self.ticket_file))

    def test_search_ticket(self):
        ticket = self.manager.create_ticket('Test User', 'IT', 'Password Reset', 'Service Request', ticket_type='Service Request')
        found = self.manager.search_by_id(ticket.ticket_id)
        self.assertEqual(found.ticket_id, ticket.ticket_id)

    def test_update_ticket_status(self):
        ticket = self.manager.create_ticket('Test User', 'IT', 'Internet Down', 'Incident')
        updated = self.manager.update_ticket(ticket.ticket_id, status='In Progress')
        self.assertEqual(updated.status, 'In Progress')

    def test_close_ticket(self):
        ticket = self.manager.create_ticket('Test User', 'IT', 'Disk Full', 'Incident')
        closed = self.manager.close_ticket(ticket.ticket_id)
        self.assertEqual(closed.status, 'Closed')
        self.assertIsNotNone(closed.resolved_date)

    def test_delete_ticket(self):
        ticket = self.manager.create_ticket('Test User', 'IT', 'Laptop Slow', 'Service Request', ticket_type='Service Request')
        deleted = self.manager.delete_ticket(ticket.ticket_id)
        self.assertEqual(deleted.ticket_id, ticket.ticket_id)
        with self.assertRaises(TicketError):
            self.manager.search_by_id(ticket.ticket_id)

    def test_backup_csv(self):
        self.manager.create_ticket('Test User', 'IT', 'Application Crash', 'Incident')
        backup_path = self.manager.backup_to_csv()
        self.assertTrue(os.path.exists(backup_path))

    def test_sla_breach(self):
        ticket = self.manager.create_ticket('Test User', 'IT', 'Server Down', 'Incident')
        ticket.sla_deadline = '2000-01-01T00:00:00'
        self.assertTrue(self.manager.sla_breaches())

    def test_monitor_ticket_creation(self):
        monitor = Monitor(self.manager)
        if hasattr(monitor, 'scan_resources'):
            result = monitor.scan_resources()
            self.assertIsInstance(result, dict)

    def test_invalid_ticket_id(self):
        with self.assertRaises(TicketError):
            self.manager.search_by_id('TKT-999')


if __name__ == '__main__':
    unittest.main()
