#!/usr/bin/env python3
"""
ChromaDB Dashboard with CORS Proxy
This server serves the dashboard and proxies API requests to ChromaDB with proper CORS headers.
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
import json
import webbrowser
import sys
import os
from pathlib import Path

DASHBOARD_PORT = 3001
CHROMADB_URL = "http://localhost:8000"
DASHBOARD_FILE = "chromadb-dashboard.html"

class ChromaDBProxyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self.proxy_request()
        else:
            self.send_error(404)

    def proxy_request(self):
        try:
            # Build the target URL
            target_url = f"{CHROMADB_URL}{self.path}"
            
            # Get request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create the request with the same method
            req = urllib.request.Request(target_url, method=self.command)
            req.add_header('Content-Type', 'application/json')
            
            if request_body:
                req.data = request_body
            
            # Make the request
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                
                # Send response
                self.send_response(response.getcode())
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_data)
                
        except urllib.error.HTTPError as e:
            error_data = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(error_data)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e)}).encode()
            self.wfile.write(error_response)

def main():
    # Change to the directory containing the dashboard
    dashboard_path = Path(__file__).parent / DASHBOARD_FILE
    
    if not dashboard_path.exists():
        print(f"❌ Error: {DASHBOARD_FILE} not found in current directory")
        print(f"   Expected location: {dashboard_path}")
        sys.exit(1)
    
    # Change to the directory containing the dashboard
    os.chdir(Path(__file__).parent)
    
    try:
        with socketserver.TCPServer(("", DASHBOARD_PORT), ChromaDBProxyHandler) as httpd:
            print(f"🚀 Starting ChromaDB Dashboard with CORS Proxy...")
            print(f"📊 Dashboard available at: http://localhost:{DASHBOARD_PORT}")
            print(f"🔗 Proxying API requests to: {CHROMADB_URL}")
            print(f"🌐 Serving from: {os.getcwd()}")
            print(f"📁 Dashboard file: {DASHBOARD_FILE}")
            print("")
            print("Press Ctrl+C to stop the server")
            print("")
            
            # Open the dashboard in the default browser
            webbrowser.open(f"http://localhost:{DASHBOARD_PORT}/{DASHBOARD_FILE}")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {DASHBOARD_PORT} is already in use")
            print("   Try using a different port or stop the conflicting service")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
