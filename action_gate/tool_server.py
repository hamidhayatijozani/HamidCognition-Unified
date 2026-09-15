from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

class Tool(BaseHTTPRequestHandler):
    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(size) or b"{}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"tool_executed": True, "received": body}).encode())

ThreadingHTTPServer(("127.0.0.1", 9000), Tool).serve_forever()
