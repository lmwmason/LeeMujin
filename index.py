from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response_data = {"message": "LeeMujin API - Root"}
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))