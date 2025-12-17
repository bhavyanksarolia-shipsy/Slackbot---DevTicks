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

def format_pod_stage_summary(data):
    lines = []

    for pod, pod_data in data.items():
        total = pod_data.get("total", 0)

        # Skip empty pods
        if total == 0:
            continue

        # POD heading
        lines.append(f"*{pod}* ({total})")

        # Stage breakdown
        for stage, count in pod_data.get("stages", {}).items():
            readable_stage = stage.replace("_", " ").title()
            lines.append(f"    • {readable_stage} — {count}")

        # Blank line between pods
        lines.append("")

    return "\n".join(lines).strip()


def post_message_on_start(summary):

    if not CHANNEL_ID:
        print("CHANNEL_ID is missing. Add it to your .env file.")
        return

    if not summary:
        text = "Hello <@{}>! No ticket data found.".format(USER_ID)
    else:
        formatted_text = format_pod_stage_summary(summary)
        text = (
            f"Hello <@{USER_ID}>! 👋\n\n"
            f"*Ticket Summary by POD*\n\n"
            f"{formatted_text}"
        )

    app.client.chat_postMessage(
        channel=CHANNEL_ID,
        text=text
    )

if __name__ == "__main__":
    result = fetch_devrev_tickets()

    post_message_on_start(result)

    # Keep Slack app alive
    SocketModeHandler(app, SLACK_APP_TOKEN).start()