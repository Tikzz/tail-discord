from subprocess import Popen, PIPE, STDOUT
import json
import time
import re
import sys
import requests

cmd = sys.argv[1].split(" ")
webhook_id = sys.argv[2]
webhook_token = sys.argv[3]

webhook_name = "Server logs"
webhook_avatar = (
    "https://cdn2.iconfinder.com/data/icons/greenline/512/heartbeat-512.png"
)
webhook_url = f"https://discordapp.com/api/webhooks/{webhook_id}/{webhook_token}"

highlights = [("Finished loading", "green"), ("ran command", "orange")]
colors = {"green": "css", "orange": "fix"}
buffer_lines = []

p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
for line in p.stdout:
    txt = line.decode("utf-8").strip()

    if txt != "":
        # Remove date, hostname and process (journalctl/systemd logs)
        f = re.search("kotoura.*\]: (.*)", txt)
        if f:
            txt = f.group(1)

        msg_color = None
        highlight = False

        for h, color in highlights:
            if h in txt:
                highlight = True
                msg_color = colors[color]

        msg = f"```{msg_color}\n {txt}```" if highlight else f"`{txt}`"

        buffer_lines.append(msg)

        if len(buffer_lines) >= 5:
            webhook_data = {
                "username": webhook_name,
                "avatar_url": webhook_avatar,
                "content": "\n".join(buffer_lines),
            }

            while True:
                r = requests.post(
                    webhook_url, data=[("payload_json", json.dumps(webhook_data))]
                )
                limit_remaining = int(r.headers["X-RateLimit-Remaining"])
                limit_reset = int(r.headers["X-RateLimit-Reset"])
                if limit_remaining == 0:
                    time.sleep(limit_reset - time.time() + 1)
                if r.status_code != 429:
                    break

            time.sleep(0.5)
            buffer_lines = []

