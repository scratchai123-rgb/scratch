import scratchattach as sa
import anthropic
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

username = os.environ["SCRATCH_USERNAME"]
password = os.environ["SCRATCH_PASSWORD"]
api_key = os.environ["ANTHROPIC_KEY"]

print("Starting bot...")

# Claude client
client = anthropic.Anthropic(api_key=api_key)

print("Logging into Scratch...")
session = sa.login(username, password)
print("Logged in!")

print("Connecting to cloud...")
cloud = session.connect_cloud(1298059856)  # project id as number
print("Connected!")

# CREATE REQUEST HANDLER (correct way)
requests = sa.CloudRequests(cloud)

@requests.request
def chat(message):
    print("Received message:", message)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content": message}]
    )

    reply = response.content[0].text
    print("Sending reply:", reply)

    return reply

@requests.event
def on_ready():
    print("Bot is ready and listening!")

# Simple web server (keeps Render alive)
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=run_server).start()
print("Web server started!")

# START LISTENER
print("Starting cloud requests...")
requests.run()

while True:
    time.sleep(1)
