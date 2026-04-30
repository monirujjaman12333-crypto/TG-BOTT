import threading
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import requests

# ✅ Port reuse fix
socketserver.TCPServer.allow_reuse_address = True

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8369733496:AAFQMCynGk3I3IO3jaK13P6nlT0KCMSru00")

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

def delete_webhook():
    """শুরুতেই webhook ও pending updates মুছে দাও — Conflict এড়াতে"""
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
            json={"drop_pending_updates": True},
            timeout=10
        )
        print(f"✅ Webhook deleted: {r.json()}")
    except Exception as e:
        print(f"⚠️ deleteWebhook error: {e}")

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
    # 1. Webhook + pending updates মুছো — সবার আগে
    delete_webhook()

    # 2. Health server
    threading.Thread(target=run_health_server, daemon=True).start()

    # 3. OTP Monitor — background thread
    threading.Thread(target=run_otp_monitor, daemon=True).start()

    # 4. Bot — main thread এ চালাও
    run_bot()
