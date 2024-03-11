import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import MagicParser

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# constants
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
DEFAULT_RESPONSE = "Didn't quite get that. Try '@CardBot -h' for help."
HELP_TEXT = """
To request details on a Magic: the Gathering card with CardBot, use "@CardBot get <cardname>."
More functionality potentially coming soon!
"""

@app.event("app_mention")
def handle_mention(event):
    message = event["text"]
    print(message)
    cmd = strip_bot_mention(message)
    args = cmd.split()
    response = None
    flags = []
    for arg in args:
        if arg.startswith("-"):
            flags.append(arg)
            args.remove(arg)
    if (args and args[0].lower() == "help") or (flags and "-h" in flags):
        response = HELP_TEXT
    if not response and cmd.startswith("get"):
        args.remove("get")
        args = " ".join(args)
        response = MagicParser.parse_magic_card(args)
    app.client.chat_postMessage(channel=event["channel"], text=response or DEFAULT_RESPONSE, thread_ts=event.get("thread_ts"))

def strip_bot_mention(message_text):
    """
    Finds direct mentions (mentions at the front of a message)
    :param message_text: The message text
    :return: User ID mentioned, or if no direct mention, None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return matches.group(2).strip() if matches else None

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()