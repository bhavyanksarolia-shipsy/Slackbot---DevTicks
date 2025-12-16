import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from fetch import fetch_devrev_tickets

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USER_ID = os.getenv("USER_ID")

app = App(token=SLACK_BOT_TOKEN)

def post_message_on_start(argument):
    if not CHANNEL_ID:
        print("CHANNEL_ID is missing. Add it to your .env file.")
        return

    if argument :
        app.client.chat_postMessage(
            channel=CHANNEL_ID,
            # text=f"Hello <@{USER_ID}>! Your Slack bot has arrived.\n {argument}",
            text=f"Hello <@{USER_ID}>! Your Slack bot has arrived, - testing"
        )
    else : 
        app.client.chat_postMessage(
            channel=CHANNEL_ID,
            # text=f"Hello <@{USER_ID}>! Your Slack bot has arrived.\n {argument}",
            text=f"Hello <@{USER_ID}>! Your Slack bot has arrived,"
        )


if __name__ == "__main__":
    # Fetch tickets and print ONLY the data field
    result = fetch_devrev_tickets()
    # print(result)
    print(len(result["works"]))

    if result :
        # Post Slack message
        post_message_on_start(result)
    else :
        post_message_on_start("No data found")

    # Keep Slack app alive
    SocketModeHandler(app, SLACK_APP_TOKEN).start()