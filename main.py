import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

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
    server.serve_forever()

# আপনার bot code এর আগে এটি যোগ করুন
thread = threading.Thread(target=run_health_server, daemon=True)
thread.start()

# এরপর আপনার bot start করুন
# bot.polling() বা app.run_polling() ইত্যাদি
