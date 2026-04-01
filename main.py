import scratchattach as sa
import anthropic
import os

username = os.environ["SCRATCH_USERNAME"]
password = os.environ["SCRATCH_PASSWORD"]
api_key = os.environ["ANTHROPIC_KEY"]

client = anthropic.Anthropic(api_key=api_key)
session = sa.login(username, password)
cloud = session.connect_cloud("1298059856")
events = cloud.events()

def decode(encoded):
    encoded = str(int(encoded))
    if len(encoded) % 2 != 0:
        encoded = "0" + encoded
    text = ""
    for i in range(0, len(encoded), 2):
        num = int(encoded[i:i+2])
        if num > 0:
            text += chr(num + 96)
    return text

def encode(text):
    result = ""
    for char in text.lower():
        code = ord(char) - 96
        if 1 <= code <= 26:
            result += str(code).zfill(2)
        else:
            result += "00"
    return str(int(result)) if result else "0"

@events.event
def on_set(activity):
    if activity.var == "message":
        message = decode(activity.value)
        if message:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=100,
                messages=[{"role": "user", "content": message}]
            )
            reply = response.content[0].text
            encoded_reply = encode(reply)
            cloud.set_var("response", encoded_reply)

events.start()

import time
while True:
    time.sleep(1)
