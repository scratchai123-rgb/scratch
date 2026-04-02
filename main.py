import scratchattach as sa
import anthropic
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

print("Starting bot...", flush=True)

# ENV VARIABLES
username = os.environ["SCRATCH_USERNAME"]
password = os.environ["SCRATCH_PASSWORD"]
api_key = os.environ["ANTHROPIC_KEY"]
project_id = 1298085384
# CLAUDE CLIENT
client = anthropic.Anthropic(api_key=api_key)

# LOGIN
print("Logging into Scratch...", flush=True)
session = sa.login(username, password)
print("Logged in!", flush=True)

# CONNECT TO CLOUD
print("Connecting to cloud...", flush=True)
cloud = session.connect_cloud(project_id)
print("Connected to cloud!", flush=True)

# CREATE REQUEST HANDLER
requests = cloud.requests()
print("Requests handler created!", flush=True)

# REQUEST FUNCTION
@requests.request
def chat(message):
    print("Received message:", message, flush=True)
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[{"role": "user", "content": message}]
        )
        reply = response.content[0].text.strip()

        # Scratch cloud vars only support numbers.
        # scratchattach encodes text automatically, but keep replies SHORT.
        # Truncate to ~100 chars to avoid encoding issues.
        if len(reply) > 100:
            reply = reply[:97] + "..."

        print("Sending reply:", reply, flush=True)
        return reply

    except Exception as e:
        print("Claude error:", e, flush=True)
        return "Error"

# EVENTS
@requests.event
def on_request(req):
    print("Incoming request:", req.name, req.args, flush=True)

@requests.event
def on_ready():
    print("Bot is ready and listening!", flush=True)

# RENDER KEEP-ALIVE SERVER
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running")

    def log_message(self, format, *args):
        return  # silence request logs

def run_server():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting web server on port {port}...", flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

# START WEB SERVER IN BACKGROUND
threading.Thread(target=run_server, daemon=True).start()

# START CLOUD LISTENER — use thread=False so the main thread stays alive
# (thread=True can cause the script to exit immediately on some hosts)
print("Starting cloud request listener...", flush=True)
requests.start(thread=False)  # This blocks — keeps the bot alive
