
Copy

import scratchattach as sa
import anthropic
import os
import re
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
 
# MARKDOWN STRIPPER
def strip_markdown(text):
    text = re.sub(r'#+\s*', '', text)               # remove headings
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)  # remove bold/italic
    text = re.sub(r'`.*?`', '', text)               # remove inline code
    text = re.sub(r'\n+', ' ', text)                # newlines to spaces
    text = re.sub(r'\s+', ' ', text)                # collapse extra spaces
    return text.strip()
 
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
            max_tokens=200,
            system="You are a helpful assistant. Keep all your responses to 200 characters or less. Be concise and clear. Never use markdown formatting like #, **, or backticks." ,
            messages=[{"role": "user", "content": message}]
        )
        reply = strip_markdown(response.content[0].text)
 
        # Safety truncation just in case
        if len(reply) > 200:
            reply = reply[:197] + "..."
 
        print("Sending reply:", reply, flush=True)
        return reply
 
    except Exception as e:
        print("Claude error:", e, flush=True)
        return "Error generating reply"
 
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
 
# START CLOUD LISTENER (blocks main thread to keep bot alive)
print("Starting cloud request listener...", flush=True)
requests.start(thread=False)
