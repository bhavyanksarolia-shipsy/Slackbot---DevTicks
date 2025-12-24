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

def get_poc_user_ids(pod, stage):
    pod_key = pod.upper().replace(" ", "_")
    stage_key = stage.upper().replace(" ", "_")

    env_key = f"POC_{pod_key}_{stage_key}"
    raw_value = os.getenv(env_key)

    # print(f"[DEBUG] {env_key} = {raw_value}")
    # print(f"{stage} - {stage_key}\n")
    # print(f"{pod} - {pod_key}\n")
    # print(f"{env_key}\n")

    if not raw_value:
        return []

    return [uid.strip() for uid in raw_value.split(",") if uid.strip()]

def format_pod_stage_summary(data):
    # print("[DEBUG] inside format_pod_stage_summary")

    lines = []

    for pod, pod_data in data.items():
        total = pod_data.get("total", 0)
        if total == 0:
            continue

        lines.append(f"*{pod}* ({total})")

        for stage, count in pod_data.get("stages", {}).items():
            readable_stage = stage.replace("_", " ").title()
            poc_user_ids = get_poc_user_ids(pod, stage)

            if poc_user_ids:
                poc_mentions = " ".join(f"<@{uid}>" for uid in poc_user_ids)
            else:
                poc_mentions = "_POC not defined_"

            lines.append(
                f"    • {readable_stage} — {count} | POC: {poc_mentions}"
            )

        lines.append("")

    return "\n".join(lines).strip()

def post_message_on_start(summary):
    if not CHANNEL_ID:
        print("CHANNEL_ID missing")
        return

    if not summary:
        text = f"Hello <@{USER_ID}>! No ticket data found."
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
    SocketModeHandler(app, SLACK_APP_TOKEN).start()