import scratchattach as sa
import anthropic
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

username = os.environ["SCRATCH_USERNAME"]
password = os.environ["SCRATCH_PASSWORD"]
api_key = os.environ["ANTHROPIC_KEY"]
print("test")

print("Logging into Scratch...")
client = anthropic.Anthropic(api_key=api_key)
session = sa.login(username, password)
print("Logged in!")
cloud = session.connect_cloud("1298059856")
print("Connected to cloud!")
requests = cloud.requests()
print("Requests handler created!")

@requests.request
def chat(message):
    print(f"Received message: {message}")
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content": message}]
    )
    return response.content[0].text

@requests.event
def on_ready():
    self.wfile.write(b"Bot is running! Requests handler is active.")

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

try:
    requests.start(thread=True)
    print("Requests handler started!")
except Exception as e:
    print(f"Error starting requests handler: {e}")

while True:
    time.sleep(1)
