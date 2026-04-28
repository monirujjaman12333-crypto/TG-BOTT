import threading
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# ✅ Port reuse fix — Address already in use সমস্যা দূর হবে
socketserver.TCPServer.allow_reuse_address = True

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"OK")
        self.wfile.flush()
    def log_message(self, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"✅ Health server running on port {port}")
    server.serve_forever()

def run_otp_monitor():
    try:
        import otp_monitor
        print("✅ OTP Monitor started")
        otp_monitor.main()
    except Exception as e:
        print(f"⚠️ OTP Monitor error: {e}")

def run_bot():
    try:
        import bot
        print("✅ Bot started")
        bot.main()
    except Exception as e:
        print(f"⚠️ Bot error: {e}")

if __name__ == "__main__":
    # 1. Health server — একবারই চালু হবে
    threading.Thread(target=run_health_server, daemon=True).start()

    # 2. OTP Monitor — background thread
    threading.Thread(target=run_otp_monitor, daemon=True).start()

    # 3. Bot — main thread এ চালাও
    run_bot()
