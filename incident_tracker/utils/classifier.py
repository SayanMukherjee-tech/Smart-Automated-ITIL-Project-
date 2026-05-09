
import re

# Pre-compiled regex patterns
network_pattern = re.compile(r"(\b(?:\d{1,3}\.){3}\d{1,3}\b|tcp|udp|icmp|vlan|switch|firewall)", re.IGNORECASE)
security_pattern = re.compile(r"(breach|ransomware|brute[- ]?force|malware|phishing|unauthorized)", re.IGNORECASE)
app_pattern = re.compile(r"(error code|exception|http[- ]?\d{3}|stack trace|NullPointerException)", re.IGNORECASE)

critical_kw = re.compile(r"(outage|down|breach|ransomware|production)", re.IGNORECASE)
high_kw = re.compile(r"(timeout|failing|unavailable|unreachable)", re.IGNORECASE)
medium_kw = re.compile(r"(slow|degraded|warning|intermittent)", re.IGNORECASE)

def detect_type(text: str) -> str:
	if network_pattern.search(text):
		return 'network'
	elif security_pattern.search(text):
		return 'security'
	elif app_pattern.search(text):
		return 'app'
	else:
		return 'general'

def detect_severity(text: str) -> str:
	if critical_kw.search(text):
		return 'critical'
	elif high_kw.search(text):
		return 'high'
	elif medium_kw.search(text):
		return 'medium'
	else:
		return 'low'
