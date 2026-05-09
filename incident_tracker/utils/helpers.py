
from functools import reduce

def get_critical_incidents(incidents):
	return list(filter(lambda i: i.severity == 'critical', incidents))

def build_jira_payloads(incidents):
	return list(map(lambda i: i.to_dict(), incidents))

def count_by_team(incidents):
	return reduce(
		lambda acc, i: {**acc, i.assigned_team: acc.get(i.assigned_team, 0) + 1},
		incidents, {}
	)
