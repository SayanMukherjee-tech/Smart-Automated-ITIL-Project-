import http.server
import socketserver
import json
import os
import sys

# Add project root to path so we can import from incident_tracker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from incident_tracker.main import load_incidents, process_incidents
from incident_tracker.models.report import ReportGenerator

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/classify':
            try:
                print("\n[Server] Received classification request")
                # Trigger the exact same logic as main.py
                filepath = os.path.join(os.path.dirname(__file__), "data", "incidents.json")
                incidents = load_incidents(filepath)
                processed = process_incidents(incidents)
                report_gen = ReportGenerator(processed)
                
                # Use default paths which relative to project root
                report_gen.generate_html()
                report_gen.export_json()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                print("[Server] Classification complete and reports generated")
            except Exception as e:
                print(f"[Server] Error during classification: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # We want to serve from the project root so paths like /incident_tracker/... work
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print("To stop the server, press Ctrl+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.server_close()
