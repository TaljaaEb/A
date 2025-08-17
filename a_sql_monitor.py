# a_sql_monitor.py
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- DATA ---
transactions = [
    "101 18V Cordless Drill 2 89.99",
    "102 6-inch Wood Clamp 4 12.50",
    "103 Carpenter's Hammer 1 19.99"
]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/transactions":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            for t in transactions:
                self.wfile.write(f"<item>{t}</item>\n".encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def run(server_class=HTTPServer, handler_class=Handler, host="0.0.0.0", port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print(f"[A] Serving transactions at http://{host}:{port}/transactions")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
