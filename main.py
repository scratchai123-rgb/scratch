import scratchattach as sa
import anthropic
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ENV VARIABLES
username = os.environ["SCRATCH_USERNAME"]
password = os.environ["SCRATCH_PASSWORD"]
api_key = os.environ["ANTHROPIC_KEY"]

print("Starting bot...")

# Claude client
client = anthropic.Anthropic(api_key=api_key)

# LOGIN
print("Logging into Scratch...")
session = sa.login(username, password)
print("Logged in!")

# CONNECT CLOUD
print("Connecting to cloud...")
cloud = session.connect_cloud(1298059856)
print("Connected to cloud!")

# REQUEST HANDLER
requests = cloud.requests()
print("Requests handler created!")

# CHAT FUNCTION
@requests.request
def chat(message):
    print("Received:", message)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[{"role": "user", "content": message}]
        )

        reply = response.content[0].text
        print("Reply:", reply)

        return reply

    except Exception as e:
        print("Claude error:", e)
        return "Error"

# READY EVENT
@requests.event
def on_ready():
    print("Bot is ready!")

# KEEP RENDER ALIVE
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running")

    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_server).start()
print("Web server started!")

# START REQUEST LISTENER
print("Starting cloud requests...")
requests.start(thread=True)

# KEEP PROCESS ALIVE
while True:
    time.sleep(1)
