import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load .env variables
load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Channel + User
CHANNEL_ID = os.environ.get("CHANNEL_ID")
USER_ID = os.environ.get("USER_ID")

# MESSAGE_TO_POST = "@bhavyank.sarolia Slack bot has arrived. No triggers. Just vibes."

# Post message
def post_message_on_start():
    if CHANNEL_ID:
        app.client.chat_postMessage(
            channel=CHANNEL_ID,
            text=f"Hello <@{USER_ID}>! Your Slack bot has arrived."
        )
    else:
        print("CHANNEL_ID is missing. Add it to your .env file.")

if __name__ == "__main__":
    # Post the message BEFORE starting Socket Mode
    post_message_on_start()

    # Start Socket Mode (does nothing for us except keep the app alive)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()