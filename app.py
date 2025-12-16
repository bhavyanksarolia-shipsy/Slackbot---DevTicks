import os
import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USER_ID = os.getenv("USER_ID")
DEVREV_API_TOKEN = os.getenv("DEVREV_API_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

DEVREV_API_URL = "https://api.devrev.ai/works.list"

REQUEST_BODY = {
    "type": "ticket",
    "ticket": {
        "subtype": "Support"
    },
    "limit":1,
    "stage": {
        "name": [
            "awaiting_customer_response",
            "queued",
            "awaiting_development",
            "in_development",
            "work_in_progress",
            "Reopen",
            "awaiting_product_assist",
            "Reassigned to Customer Support",
        ]
    },
    "custom_fields": {
        "tnt__pod": ["WMS Inbound"]
    }
}

REQUEST_HEADERS = {
    "Authorization": f"Bearer {DEVREV_API_TOKEN}",
    "Content-Type": "application/json",
}

def fetch_devrev_tickets():
    response = requests.post(
        DEVREV_API_URL,
        headers=REQUEST_HEADERS,
        json=REQUEST_BODY
    )
    response.raise_for_status()
    return response.json()


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