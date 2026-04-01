import scratchattach as sa
from scratchattach.cloud_requests import CloudRequests
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

# CONNECT TO CLOUD
print("Connecting to cloud...")
cloud = session.connect_cloud(1298059856)
print("Connected to cloud!")

# CREATE REQUEST HANDLER
requests = CloudRequests(cloud)
print("Requests handler created!")

# CHAT REQUEST
@requests.request
def chat(message):
    print("Received message:", message)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[
                {"role": "user", "content": message}
            ]
        )

        reply = response.content[0].text
        print("Sending reply:", reply)

        return reply

    except Exception as e:
        print("Claude error:", e)
        return "Error"

# READY EVENT
@requests.event
def on_ready():
    print("Bot is ready and listening!")

# KEEP-ALIVE SERVER (required for Render)
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

# START CLOUD REQUEST LISTENER
print("Starting cloud requests...")
requests.run(thread=True)

# KEEP PROCESS ALIVE
while True:
    time.sleep(1)
