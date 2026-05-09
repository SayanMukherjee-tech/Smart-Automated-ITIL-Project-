# ReportGenerator class will be implemented here

import json
import os
from collections import Counter

class ReportGenerator:
    def __init__(self, incidents):
        self.incidents = incidents

    def _incident_type(self, incident):
        return type(incident).__name__.replace('Incident', '')

    def _severity_badge(self, severity):
        classes = {
            'critical': 'severity-badge critical',
            'high': 'severity-badge high',
            'medium': 'severity-badge medium',
            'low': 'severity-badge low'
        }
        return f'<span class="{classes.get(severity, "severity-badge")}">{severity.upper()}</span>'

    def _build_chip(self, label, count):
        return f'<span class="chip">{label} <strong>{count}</strong></span>'

    def generate_html(self, output_path="index.html"):
        incidents = sorted(self.incidents)
        total = len(incidents)
        severity_counts = Counter(i.severity for i in incidents)
        type_counts = Counter(self._incident_type(i) for i in incidents)
        team_counts = Counter(i.assigned_team for i in incidents)

        type_chips = ''.join(self._build_chip(label, count) for label, count in type_counts.items())
        severity_chips = ''.join(self._build_chip(label.capitalize(), count) for label, count in severity_counts.items())
        team_chips = ''.join(self._build_chip(label, count) for label, count in team_counts.items())

        rows = ''
        for inc in incidents:
            severity = inc.severity or 'unknown'
            ticket_snow = inc.ticket_ids.get('servicenow', '-')
            ticket_jira = inc.ticket_ids.get('jira', '-')
            ticket_azure = inc.ticket_ids.get('azure', '-')
            rows += f"""
            <tr>
                <td>{inc.id}</td>
                <td>{inc.title}</td>
                <td>{self._severity_badge(severity)}</td>
                <td>{self._incident_type(inc)}</td>
                <td>{inc.assigned_team}</td>
                <td>{ticket_snow}</td>
                <td>{ticket_jira}</td>
                <td>{ticket_azure}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>IT Incident Auto-Triage Report</title>
    <style>
        :root {{
            color-scheme: light;
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: #f2f6fb;
            color: #102a4e;
        }}

        * {{ box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; background: #eef3fb; }}
        .page-shell {{ max-width: 1320px; margin: 0 auto; padding: 24px 28px 40px; }}
        .page-header {{ background: #1f3f70; color: #ffffff; border-radius: 24px; padding: 28px 32px; box-shadow: 0 18px 50px rgba(15, 38, 79, 0.12); }}
        .page-header h1 {{ margin: 0; font-size: 2rem; letter-spacing: -0.03em; }}
        .page-header p {{ margin: 10px 0 0; color: #d7e3ff; font-size: 1rem; max-width: 720px; line-height: 1.6; }}
        .summary-cards {{ display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 18px; margin: 26px 0 20px; }}
        .card {{ background: #ffffff; border-radius: 22px; padding: 22px 24px; box-shadow: 0 14px 32px rgba(15, 38, 79, 0.08); }}
        .card.total {{ background: linear-gradient(135deg, #1d4ede 0%, #1c6ce8 100%); color: #f7fbff; }}
        .card-label {{ display: block; font-size: 0.88rem; letter-spacing: 0.04em; opacity: 0.82; margin-bottom: 12px; }}
        .card-value {{ font-size: 2.65rem; font-weight: 700; line-height: 1; }}
        .card.count {{ color: #102a4e; }}
        .card.critical .card-value {{ color: #d33c48; }}
        .card.high .card-value {{ color: #f08f00; }}
        .card.medium .card-value {{ color: #ffb100; }}
        .card.low .card-value {{ color: #2e7d32; }}

        .breakdown-panels {{ display: grid; grid-template-columns: repeat(3, minmax(240px, 1fr)); gap: 18px; margin-bottom: 28px; }}
        .panel {{ background: #ffffff; border-radius: 20px; padding: 22px 24px; box-shadow: 0 16px 36px rgba(15, 38, 79, 0.06); }}
        .panel h2 {{ margin: 0 0 16px; font-size: 1rem; letter-spacing: 0.02em; text-transform: uppercase; color: #1d3b6f; }}
        .chips {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .chip {{ display: inline-flex; align-items: center; gap: 8px; padding: 11px 16px; border-radius: 999px; background: #f7f9fd; color: #102a4e; font-size: 0.95rem; font-weight: 600; border: 1px solid #dfe7f4; }}
        .chip strong {{ color: #1d3b6f; }}

        .table-shell {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 900px; background: #ffffff; border-radius: 22px; overflow: hidden; box-shadow: 0 20px 54px rgba(15, 38, 79, 0.08); }}
        thead {{ background: #12264b; }}
        th, td {{ padding: 18px 20px; text-align: left; }}
        th {{ color: #f4f7ff; font-size: 0.92rem; letter-spacing: 0.04em; text-transform: uppercase; border-bottom: 1px solid rgba(255, 255, 255, 0.12); }}
        tbody tr {{ transition: background 0.2s ease; }}
        tbody tr:nth-child(even) {{ background: #f7f9ff; }}
        tbody tr:hover {{ background: #edf4ff; }}
        td {{ color: #21335b; border-bottom: 1px solid #e9eef8; vertical-align: middle; }}

        .severity-badge {{ display: inline-flex; align-items: center; justify-content: center; padding: 8px 12px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; }}
        .severity-badge.critical {{ background: #ffe9ea; color: #bf1f2d; }}
        .severity-badge.high {{ background: #fff3e4; color: #dc7d12; }}
        .severity-badge.medium {{ background: #fff9e6; color: #b8800f; }}
        .severity-badge.low {{ background: #e9f5eb; color: #2d7b35; }}

        .footer {{ margin-top: 28px; font-size: 0.92rem; color: #6b7a96; text-align: center; }}
        .classify-button {{ background: #ffffff; color: #1d3b6f; border: none; padding: 12px 20px; border-radius: 12px; font-weight: 600; font-size: 0.95rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.1); font-family: inherit; }}
        .classify-button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.15); }}
        .classify-button:active {{ transform: translateY(0); }}
        .classify-button.loading {{ opacity: 0.8; cursor: not-allowed; }}
        @media (max-width: 960px) {{ .summary-cards, .breakdown-panels {{ grid-template-columns: repeat(2, minmax(180px, 1fr)); }} }}
        @media (max-width: 680px) {{ .summary-cards, .breakdown-panels {{ grid-template-columns: 1fr; }} th, td {{ padding: 14px 12px; }} .page-header > div {{ flex-direction: column; gap: 16px; }} }}
    </style>
</head>
<body>
    <div class="page-shell">
        <div class="page-header">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div>
                    <h1>IT Incident Auto-Triage Report</h1>
                    <p>Summary dashboard for incident triage across ServiceNow, Jira, and Azure Boards. Track incident type, severity, assignment, and ticket delivery in one view.</p>
                </div>
                <button id="classify-btn" class="classify-button">
                    <span id="btn-icon">🔄</span> <span id="btn-text">Auto-Classify New Tickets</span>
                </button>
            </div>
        </div>

        <div class="summary-cards">
            <div class="card total">
                <span class="card-label">Total Incidents</span>
                <span class="card-value">{total}</span>
            </div>
            <div class="card critical">
                <span class="card-label">Critical</span>
                <span class="card-value">{severity_counts.get('critical', 0)}</span>
            </div>
            <div class="card high">
                <span class="card-label">High</span>
                <span class="card-value">{severity_counts.get('high', 0)}</span>
            </div>
            <div class="card medium">
                <span class="card-label">Medium</span>
                <span class="card-value">{severity_counts.get('medium', 0)}</span>
            </div>
        </div>

        <div class="breakdown-panels">
            <div class="panel">
                <h2>Breakdown by Type</h2>
                <div class="chips">{type_chips}</div>
            </div>
            <div class="panel">
                <h2>Breakdown by Severity</h2>
                <div class="chips">{severity_chips}</div>
            </div>
            <div class="panel">
                <h2>Breakdown by Team</h2>
                <div class="chips">{team_chips}</div>
            </div>
        </div>

        <div class="table-shell">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Team</th>
                        <th>ServiceNow</th>
                        <th>Jira</th>
                        <th>Azure Boards</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>

        <div class="footer">Generated by IT Incident Auto-Triage & Tracker</div>
    </div>
    <script>
        // JS Version of your Python Triage Logic
        const patterns = {{
            network: /(\b(?:\d{{1,3}}\.){{3}}\d{{1,3}}\b|tcp|udp|icmp|vlan|switch|firewall)/i,
            security: /(breach|ransomware|brute[- ]?force|malware|phishing|unauthorized)/i,
            app: /(error code|exception|http[- ]?\d{{3}}|stack trace|NullPointerException)/i,
            critical: /(outage|down|breach|ransomware|production)/i,
            high: /(timeout|failing|unavailable|unreachable)/i,
            medium: /(slow|degraded|warning|intermittent)/i
        }};

        function classify(title, desc) {{
            const text = title + " " + desc;
            let type = 'general';
            if (patterns.network.test(text)) type = 'Network';
            else if (patterns.security.test(text)) type = 'Security';
            else if (patterns.app.test(text)) type = 'App';

            let severity = 'low';
            if (patterns.critical.test(text)) severity = 'critical';
            else if (patterns.high.test(text)) severity = 'high';
            else if (patterns.medium.test(text)) severity = 'medium';

            return {{ type, severity }};
        }}

        async function handleClassify() {{
            const btn = document.getElementById('classify-btn');
            const btnText = document.getElementById('btn-text');
            const btnIcon = document.getElementById('btn-icon');
            
            btn.classList.add('loading');
            btnText.innerText = 'Classifying...';
            btnIcon.innerText = '⏳';
            btn.disabled = true;

            // 1. Try local Python backend first
            try {{
                const response = await fetch('/classify', {{ method: 'POST' }});
                if (response.ok) {{
                    btnText.innerText = 'Success! Reloading...';
                    btnIcon.innerText = '✅';
                    setTimeout(() => location.reload(), 1000);
                    return;
                }}
            }} catch (err) {{
                console.log("Local server not found, falling back to client-side logic.");
            }}

            // 2. Fallback for Static Deployment (GitHub Pages)
            try {{
                const res = await fetch('incident_tracker/data/incidents.json?t=' + Date.now());
                if (!res.ok) throw new Error("Fetch failed: " + res.status);
                const data = await res.json();
                
                updateTable(data);
                
                btnText.innerText = 'Client-Side Success!';
                btnIcon.innerText = '✅';
                btn.disabled = false;
                btn.classList.remove('loading');
            }} catch (err) {{
                btnText.innerText = 'Error: ' + err.message;
                btnIcon.innerText = '❌';
                btn.disabled = false;
                btn.classList.remove('loading');
                console.error("Classification error:", err);
            }}
        }}

        function updateTable(incidents) {{
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = '';
            
            let counts = {{ total: incidents.length, critical: 0, high: 0, medium: 0, low: 0 }};
            
            incidents.forEach(inc => {{
                const res = classify(inc.title, inc.description);
                counts[res.severity]++;
                
                const row = `
                    <tr>
                        <td>${{inc.id}}</td>
                        <td>${{inc.title}}</td>
                        <td><span class="severity-badge ${{res.severity}}">${{res.severity.toUpperCase()}}</span></td>
                        <td>${{res.type}}</td>
                        <td>${{inc.assigned_team}}</td>
                        <td>MOCK-SNOW-${{inc.id}}</td>
                        <td>MOCK-JIRA-${{inc.id}}</td>
                        <td>MOCK-AZURE-${{inc.id}}</td>
                    </tr>`;
                tbody.innerHTML += row;
            }});

            // Update Dashboard Cards
            document.querySelector('.card.total .card-value').innerText = counts.total;
            document.querySelector('.card.critical .card-value').innerText = counts.critical;
            document.querySelector('.card.high .card-value').innerText = counts.high;
            document.querySelector('.card.medium .card-value').innerText = counts.medium;
        }}

        document.getElementById('classify-btn').addEventListener('click', handleClassify);
    </script>
</body>
</html>"""

        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"HTML report generated: {output_path}")

    def export_json(self, output_path="incident_tracker/output/report.json"):
        data = [inc.to_dict() for inc in self.incidents]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"JSON report generated: {output_path}")
