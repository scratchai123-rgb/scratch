import scratchattach as sa
from openai import OpenAI
import os
import re
import time
import threading
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

print("Starting bot...", flush=True)

# ENV VARIABLES
username = os.environ["SCRATCH_USERNAME"]
password = os.environ["SCRATCH_PASSWORD"]

# KEEP SAME ENV VARIABLE NAME
api_key = os.environ["ANTHROPIC_KEY"]

project_id = 1298085384

# OPENAI CLIENT
client = OpenAI(api_key=api_key)

# MARKDOWN STRIPPER
def strip_markdown(text):
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# SELF-PING
def keep_alive():
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        print("No RENDER_EXTERNAL_URL set, skipping keep-alive pings.", flush=True)
        return

    while True:
        time.sleep(600)

        try:
            urllib.request.urlopen(url)
            print("Keep-alive ping sent.", flush=True)

        except Exception as e:
            print("Keep-alive ping failed:", e, flush=True)

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
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Keep all responses under 200 characters. "
                        "Be concise and clear. "
                        "Do not use markdown formatting."
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=100
        )

        reply = response.choices[0].message.content
        reply = strip_markdown(reply)

        # Safety truncation
        if len(reply) > 200:
            reply = reply[:197] + "..."

        print("Sending reply:", reply, flush=True)
        return reply

    except Exception as e:
        print("OpenAI error:", e, flush=True)
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
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting web server on port {port}...", flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

# START WEB SERVER
threading.Thread(target=run_server, daemon=True).start()

# START KEEP-ALIVE PINGER
threading.Thread(target=keep_alive, daemon=True).start()

# START CLOUD LISTENER
print("Starting cloud request listener...", flush=True)
requests.start(thread=False)
