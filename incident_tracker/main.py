# CLI entry point for Incident Auto-Triage & Tracker

import json
import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.incident import NetworkIncident, AppIncident, SecurityIncident
from models.report import ReportGenerator
from utils.classifier import detect_type, detect_severity
from utils.helpers import get_critical_incidents, count_by_team
from services.servicenow import create_servicenow_ticket
from services.jira import create_jira_issue
from services.azure_boards import create_azure_work_item


def load_incidents(filepath="incident_tracker/data/incidents.json"):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    incidents = []
    for item in data:
        inc_type = detect_type(item['title'] + ' ' + item['description'])
        severity = detect_severity(item['title'] + ' ' + item['description'])
        
        if inc_type == 'network':
            inc = NetworkIncident(
                item['id'], item['title'], item['description'],
                item['reported_by'], item['timestamp'], item['assigned_team']
            )
        elif inc_type == 'app':
            inc = AppIncident(
                item['id'], item['title'], item['description'],
                item['reported_by'], item['timestamp'], item['assigned_team']
            )
        elif inc_type == 'security':
            inc = SecurityIncident(
                item['id'], item['title'], item['description'],
                item['reported_by'], item['timestamp'], item['assigned_team']
            )
        else:
            # Default to NetworkIncident for general
            inc = NetworkIncident(
                item['id'], item['title'], item['description'],
                item['reported_by'], item['timestamp'], item['assigned_team']
            )
        
        inc._severity = severity
        incidents.append(inc)
    return incidents


def process_incidents(incidents, severity_filter=None):
    if severity_filter:
        incidents = [i for i in incidents if i.severity == severity_filter]
    
    for inc in incidents:
        print(f"Processing {inc.id}: {inc.title}")
        
        # Create tickets in all three platforms
        snow_id = create_servicenow_ticket(inc)
        jira_id = create_jira_issue(inc)
        azure_id = create_azure_work_item(inc)
        
        inc.ticket_ids['servicenow'] = snow_id
        inc.ticket_ids['jira'] = jira_id
        inc.ticket_ids['azure'] = azure_id
    
    return incidents


def main():
    parser = argparse.ArgumentParser(description="IT Incident Auto-Triage & Tracker")
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'], 
                        help='Filter incidents by severity')
    parser.add_argument('--input', default='incident_tracker/data/incidents.json',
                        help='Input JSON file path')
    args = parser.parse_args()
    
    print("Loading incidents...")
    incidents = load_incidents(args.input)
    print(f"Loaded {len(incidents)} incidents")
    
    # Show stats
    team_counts = count_by_team(incidents)
    print(f"Incidents by team: {team_counts}")
    
    critical = get_critical_incidents(incidents)
    print(f"Critical incidents: {len(critical)}")
    
    print("\nProcessing incidents and creating tickets...")
    processed = process_incidents(incidents, args.severity)
    
    print("\nGenerating reports...")
    report_gen = ReportGenerator(processed)
    report_gen.generate_html()
    report_gen.export_json()
    
    print("\nDone!")


if __name__ == "__main__":
    main()
