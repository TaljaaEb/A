# b_collector_monitor.py
import socket
import json
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

C_HOST = "127.0.0.1"  # C server IP
C_PORT = 5000

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 5051  # TCP trigger port
HTTP_PORT = 80    # HTTP trigger port (Azure App Service compatible)

# ------------------------------
# Helpers
# ------------------------------
def extract_strings_recursive(test_str, tag):
    start_idx = test_str.find("<" + tag + ">")
    if start_idx == -1:
        return []
    end_idx = test_str.find("</" + tag + ">", start_idx)
    res = [test_str[start_idx+len(tag)+2:end_idx]]
    res += extract_strings_recursive(test_str[end_idx+len(tag)+3:], tag)
    return res

def handle_transaction_pull():
    """Pull data from A and send to C."""
    try:
        r = requests.get("http://127.0.0.1:8000/transactions")
        items = extract_strings_recursive(r.text, "item")
        print(f"[B] Parsed items: {items}")
        send_to_c(items)
    except Exception as e:
        print(f"[B] Error fetching from A: {e}")

def send_to_c(transactions):
    """Send transaction list to C."""
    payload = {"source": "B", "transactions": transactions}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((C_HOST, C_PORT))
            s.sendall(json.dumps(payload).encode())
            resp = s.recv(1024)
            print(f"[B] C responded: {resp.decode()}")
    except Exception as e:
        print(f"[B] Error sending to C: {e}")

# ------------------------------
# TCP trigger server
# ------------------------------
def tcp_trigger_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LISTEN_HOST, LISTEN_PORT))
        s.listen()
        print(f"[B] Waiting for TCP trigger on port {LISTEN_PORT}...")
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode().strip()
                if data == "SUCCESS":
                    print("[B] Received SUCCESS trigger (TCP)")
                    handle_transaction_pull()
                    conn.sendall(b"ACK")

# ------------------------------
# HTTP trigger server
# ------------------------------
class TriggerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/trigger":
            print("[B] Received HTTP trigger")
            handle_transaction_pull()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Triggered transaction pull")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def http_trigger_server():
    server_address = (LISTEN_HOST, HTTP_PORT)
    httpd = HTTPServer(server_address, TriggerHandler)
    print(f"[B] Listening for HTTP trigger at http://{LISTEN_HOST}:{HTTP_PORT}/trigger")
    httpd.serve_forever()

# ------------------------------
# Entry point
# ------------------------------
if __name__ == "__main__":
    threading.Thread(target=tcp_trigger_server, daemon=True).start()
    threading.Thread(target=http_trigger_server, daemon=True).start()

    print("[B] Collector Monitor is running (TCP + HTTP triggers enabled)")
    # Block forever
    threading.Event().wait()



