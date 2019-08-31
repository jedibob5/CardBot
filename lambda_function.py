"""
CardBot Lambda function handler.
"""

import logging
import json
import MagicParser
import re
import urllib

BOT_KEY_FILE = open('bot_key.txt', 'r')
BOT_KEY = BOT_KEY_FILE.read()
SLACK_URL = 'https://slack.com/api'

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
HELP_TEXT = """
To request details on a Magic: the Gathering card with CardBot, use "@CardBot get <cardname>."
More functionality potentially coming soon!
"""


def lambda_handler(data, _context):
    """
    Handle incoming Slack messages
    :param data:
    :param _context:
    :return:
    """
    slack_event = json.loads(data['body'])['event']

    if "challenge" in slack_event:
        return slack_event["challenge"]

    if "bot_id" in slack_event:  # Prevent bot from responding to itself or other bots
        logging.warning("Ignore bot event")
        return {
            'statusCode': 200,
            'body': 'bot message ignored'
        }

    chat_action = 'chat.postMessage'
    if 'app_mention' in slack_event['type']:
        data = {
            'channel': slack_event['channel'],
            'text': get_command(slack_event['text'], )
        }
        if 'thread_ts' in slack_event:
            data['thread_ts'] = slack_event['thread_ts']

    submit_slack_request(data, chat_action)
    return {
        'statusCode': 200,
        'body': 'success'
    }


def get_command(raw_text):
    """
    Returns the response we want to send back to Slack
    :param raw_text: Raw input text
    :return: Text we want to return to Slack
    """
    _bot_user_id, message = parse_mention(raw_text)
    return handle_command(message)


def parse_mention(message_text):
    """
    Finds direct mentions (mentions at the front of a message)
    :param message_text: The message text
    :return: User ID mentioned, or if no direct mention, None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(cmd):
    """
    Executes bot command if known
    :param cmd: The command
    :return: response text of the command to send back to the channel
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
    return response or default_response  # if response is empty return default instead


def submit_slack_request(data, chat_action):
    """
    Submit request object to Slack
    :param data: dict containing request data
    :param chat_action: action type to send to slack
    :return:
    """
    # Construct the HTTP request that will be sent to the Slack API.
    request = urllib.request.Request(SLACK_URL + chat_action)
    # Add a header mentioning that the text is JSON.
    request.add_header(
        "Content-Type",
        "application/json"
    )
    request.add_header(
        "Authorization", 'Bearer {}'.format(BOT_KEY),
    )

    # Fire off the request!
    return urllib.request.urlopen(request, json.dumps(data).encode('utf-8')).read()
