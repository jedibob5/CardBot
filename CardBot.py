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
def handle_event(event, context, client, say):
    message = event["text"]
    print(message)
    cmd = strip_bot_mention(message)

    args = cmd.split()
    response = None
    flags = None
    if args[0] == "-h" or args[0].lower() == "help":
        response = HELP_TEXT
    else:
        for arg in args:
            if arg.startswith("-"):
                flags.append(arg)
                args.remove(arg)
        if cmd.startswith("get"):
            args.remove("get")
            args = " ".join(args)
            response = MagicParser.parse_magic_card(args)
    say(response or DEFAULT_RESPONSE)

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