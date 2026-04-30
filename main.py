import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ─── Health Server (Render এর জন্য) ───────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass  # Silent logging

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"✅ Health server running on port {port}")
    server.serve_forever()

# ─── Main Entry Point ─────────────────────────────────────────
if __name__ == "__main__":
    # 1. Health server thread (Render port scan এর জন্য)
    t1 = threading.Thread(target=run_health_server, daemon=True)
    t1.start()

    # 2. OTP Monitor thread (background এ চলবে)
    import otp_monitor
    t2 = threading.Thread(target=otp_monitor.main, daemon=True)
    t2.start()

    # 3. Telegram Bot (main thread এ চলবে)
    import bot
    bot.main()
