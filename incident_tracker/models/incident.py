
from datetime import datetime

class Incident:
	def __init__(self, id, title, description, reported_by, timestamp, assigned_team):
		self.id = id
		self.title = title
		self.description = description
		self.reported_by = reported_by
		self.timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
		self.assigned_team = assigned_team
		self._severity = None  # set by classify()
		self.ticket_ids = {}   # populated after API calls

	def classify(self):
		raise NotImplementedError('Subclasses must implement classify()')

	@property
	def severity(self):
		return self._severity

	def to_dict(self):
		return {
			'id': self.id,
			'title': self.title,
			'description': self.description,
			'reported_by': self.reported_by,
			'timestamp': self.timestamp.isoformat(),
			'assigned_team': self.assigned_team,
			'severity': self._severity,
			'ticket_ids': self.ticket_ids
		}

	def __str__(self):
		return f"[{self.id}] {self.title} ({self.severity})"

	def __repr__(self):
		return self.__str__()

	def __lt__(self, other):
		severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
		return severity_order.get(self.severity, 4) < severity_order.get(other.severity, 4)


class NetworkIncident(Incident):
	def __init__(self, id, title, description, reported_by, timestamp, assigned_team, affected_host=None, protocol=None):
		super().__init__(id, title, description, reported_by, timestamp, assigned_team)
		self.affected_host = affected_host
		self.protocol = protocol

	def classify(self, classifier=None):
		# classifier is a function or module for regex logic
		if classifier:
			self._severity = classifier.detect_severity(self.title + ' ' + self.description)
		else:
			self._severity = 'low'
		# Additional logic to set affected_host/protocol can be added here
		return self._severity

	def escalate(self):
		# Placeholder for escalation logic
		pass


class AppIncident(Incident):
	def __init__(self, id, title, description, reported_by, timestamp, assigned_team, app_name=None, error_code=None):
		super().__init__(id, title, description, reported_by, timestamp, assigned_team)
		self.app_name = app_name
		self.error_code = error_code

	def classify(self, classifier=None):
		if classifier:
			self._severity = classifier.detect_severity(self.title + ' ' + self.description)
		else:
			self._severity = 'low'
		return self._severity

	def get_stack_trace(self):
		# Placeholder for stack trace logic
		return "Stack trace not available."


class SecurityIncident(Incident):
	def __init__(self, id, title, description, reported_by, timestamp, assigned_team, threat_type=None, source_ip=None):
		super().__init__(id, title, description, reported_by, timestamp, assigned_team)
		self.threat_type = threat_type
		self.source_ip = source_ip

	def classify(self, classifier=None):
		if classifier:
			self._severity = classifier.detect_severity(self.title + ' ' + self.description)
		else:
			self._severity = 'low'
		return self._severity

	def notify_soc(self):
		# Placeholder for SOC notification logic
		pass


class IncidentIterator:
	def __init__(self, incidents, severity_filter=None):
		self.incidents = (
			[i for i in incidents if i.severity == severity_filter]
			if severity_filter else incidents
		)
		self.index = 0

	def __iter__(self):
		return self

	def __next__(self):
		if self.index < len(self.incidents):
			result = self.incidents[self.index]
			self.index += 1
			return result
		else:
			raise StopIteration


def batch_incidents(incidents, batch_size=3):
	"""Yield incidents in batches of batch_size."""
	for i in range(0, len(incidents), batch_size):
		yield incidents[i : i + batch_size]
