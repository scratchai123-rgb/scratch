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

# Claude client
client = anthropic.Anthropic(api_key=api_key)

print("Logging into Scratch...", flush=True)
session = sa.login(username, password)
print("Logged in!", flush=True)

print("Connecting to cloud...", flush=True)
cloud = session.connect_cloud(1298059856)
print("Connected to cloud!", flush=True)

# Create request handler
requests = cloud.requests()
print("Requests handler created!", flush=True)

@requests.request
def chat(message):
    print("Received message:", message, flush=True)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[{"role": "user", "content": message}]
        )

        reply = response.content[0].text
        print("Sending reply:", reply, flush=True)

        return reply

    except Exception as e:
        print("Claude error:", e, flush=True)
        return "Error"

@requests.event
def on_ready():
    print("Bot is ready and listening!", flush=True)

# Render keep-alive server
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running")

    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    print("Starting web server...", flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_server).start()

print("Starting cloud request listener...", flush=True)
requests.start(thread=True)

while True:
    time.sleep(1)
