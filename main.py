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

# Keep the old secret name, but put your OpenAI key inside it
api_key = os.environ["ANTHROPIC_KEY"]

project_id = 1298085384

# OPENAI CLIENT
client = OpenAI(api_key=api_key)

def strip_markdown(text):
    if not text:
        return ""

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

def keep_alive():
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        print("No RENDER_EXTERNAL_URL set, skipping keep-alive.", flush=True)
        return

    while True:
        time.sleep(600)
        try:
            urllib.request.urlopen(url, timeout=10)
            print("Keep-alive ping sent.", flush=True)
        except Exception as e:
            print("Keep-alive failed:", repr(e), flush=True)

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

print("Logging into Scratch...", flush=True)
session = sa.login(username, password)
print("Logged in!", flush=True)

print("Connecting to Scratch cloud...", flush=True)
cloud = session.connect_cloud(project_id)
print("Connected to cloud!", flush=True)

requests = cloud.requests()
print("Scratch request handler created!", flush=True)

@requests.request
def chat(message):
    print("Received message:", message, flush=True)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=100,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ChatGPT, not Claude. "
                        "You are a helpful assistant inside a Scratch project. "
                        "Keep every response under 200 characters. "
                        "Do not use markdown. Be clear and concise."
                    )
                },
                {
                    "role": "user",
                    "content": str(message)
                }
            ]
        )

        reply = response.choices[0].message.content
        reply = strip_markdown(reply)

        if len(reply) > 200:
            reply = reply[:197] + "..."

        print("Sending reply:", reply, flush=True)
        return reply

    except Exception as e:
        print("OpenAI error type:", type(e).__name__, flush=True)
        print("OpenAI error:", repr(e), flush=True)
        return "OpenAI error. Check Render logs."

@requests.event
def on_ready():
    print("Bot is ready and listening!", flush=True)

threading.Thread(target=run_server, daemon=True).start()
threading.Thread(target=keep_alive, daemon=True).start()

print("Starting Scratch cloud listener...", flush=True)
requests.start(thread=False)
