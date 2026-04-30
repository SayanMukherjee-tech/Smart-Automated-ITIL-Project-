import os
import shutil
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None

from .tickets import IncidentTicket
from .logger import log_event, action_logger

THRESHOLDS = {
    'cpu': 90,
    'memory': 95,
    'disk_percent': 90,
    'disk_free_percent': 10
}


class MonitorError(Exception):
    pass


class Monitor:
    def __init__(self, ticket_manager):
        self.ticket_manager = ticket_manager

    def _get_cpu_usage(self):
        if psutil:
            return psutil.cpu_percent(interval=1)
        raise MonitorError('psutil is required for CPU monitoring')

    def _get_memory_usage(self):
        if psutil:
            return psutil.virtual_memory().percent
        raise MonitorError('psutil is required for memory monitoring')

    def _get_disk_usage(self):
        if psutil:
            usage = psutil.disk_usage(os.getcwd())
            return usage.percent, 100 - usage.percent
        total, used, free = shutil.disk_usage(os.getcwd())
        percent = used / total * 100
        return percent, free / total * 100

    def _get_network_usage(self):
        if psutil:
            counters = psutil.net_io_counters()
            return counters.bytes_sent + counters.bytes_recv
        return 0

    @action_logger
    def scan_resources(self):
        metrics = {}
        try:
            metrics['cpu'] = self._get_cpu_usage()
            metrics['memory'] = self._get_memory_usage()
            metrics['disk_used'], metrics['disk_free_percent'] = self._get_disk_usage()
            metrics['network_bytes'] = self._get_network_usage()
        except MonitorError as exc:
            log_event('error', str(exc))
            return metrics

        alerts = []
        if metrics['cpu'] > THRESHOLDS['cpu']:
            alerts.append('CPU usage exceeded')
        if metrics['memory'] > THRESHOLDS['memory']:
            alerts.append('Memory usage exceeded')
        if metrics['disk_free_percent'] < THRESHOLDS['disk_free_percent']:
            alerts.append('Disk free space below threshold')

        if alerts:
            details = ' | '.join(alerts)
            description = f"System monitoring alert: {details}. Metrics: CPU={metrics['cpu']}%, Memory={metrics['memory']}%, DiskFree={metrics['disk_free_percent']:.1f}%"
            self.auto_create_ticket(description)
            log_event('warning', description)
        else:
            log_event('info', 'System resource levels are within normal thresholds')
        return metrics

    def auto_create_ticket(self, description):
        ticket = self.ticket_manager.create_ticket(
            employee_name='System Monitor',
            department='IT Operations',
            issue_description=f"Auto ticket: {description}",
            category='Monitoring Alert',
            ticket_type='Incident'
        )
        ticket.priority = 'P1'
        ticket.sla_deadline = ticket._compute_sla_deadline()
        self.ticket_manager._save_tickets()
        log_event('critical', f"Auto-created ticket {ticket.ticket_id} for monitoring alert")
        return ticket

    def repeat_check(self, interval_seconds=60, cycles=1):
        for _ in range(cycles):
            self.scan_resources()
            time.sleep(interval_seconds)
