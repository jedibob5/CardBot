import time
import re
from slackclient import SlackClient
import MagicParser

bot_key_file = open("bot_key.txt", "r")
bot_key = bot_key_file.read()

slack_client = SlackClient(bot_key)

cardbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
HELP_TEXT = """
To request details on a Magic: the Gathering card with CardBot, use "@CardBot get <cardname>."
More functionality potentially coming soon!
"""


def parse_bot_commands(slack_events):
    """
    Parses events from Slack API to get bot commands.
    :param slack_events: Slack events retrieved from API
    :return: If command is found, return tuple of command and channel. Otherwise, None
    """
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_mention(message_text):
    """
    Finds direct mentions (mentions at the front of a message)
    :param message_text: The message text
    :return: User ID mentioned, or if no direct mention, None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(cmd, chnl):
    """
    Executes bot command if known
    :param cmd: The command
    :param chnl: The channel
    :return: no return
    """
    # Default response
    default_response = "Didn't quite get that. Try '@CardBot -h' for help."

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

    # send response back to the channel
    slack_client.api_call("chat.postMessage",
                          channel=chnl,
                          text=response or default_response)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("CardBot initialized and running!")
        # Read bot's user ID with API
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            try:
                command, channel = parse_bot_commands(slack_client.rtm_read())
                if command:
                    handle_command(command, channel)
            except SlackClient.SlackConnectionError as e:
                print(str(e))
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Stack trace above")
