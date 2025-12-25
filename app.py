import os
from slack_sdk import WebClient
from fetch import fetch_devrev_tickets

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USER_ID = os.getenv("USER_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def get_poc_user_ids(pod, stage):
    pod_key = pod.upper().replace(" ", "_")
    stage_key = stage.upper().replace(" ", "_")
    env_key = f"POC_{pod_key}_{stage_key}"
    raw_value = os.getenv(env_key)
    if not raw_value:
        return []
    return [uid.strip() for uid in raw_value.split(",") if uid.strip()]

def format_pod_stage_summary(data):
    lines = []

    for pod, pod_data in data.items():
        total = pod_data.get("total", 0)
        if total == 0:
            continue

        lines.append(f"*{pod}* ({total})")

        for stage, count in pod_data.get("stages", {}).items():
            readable_stage = stage.replace("_", " ").title()
            poc_user_ids = get_poc_user_ids(pod, stage)
            poc_mentions = (
                " ".join(f"<@{uid}>" for uid in poc_user_ids)
                if poc_user_ids else "_POC not defined_"
            )
            lines.append(f"    • {readable_stage} — {count} {poc_mentions}")

        lines.append("")

    return "\n".join(lines).strip()

def post_summary(summary):
    if not CHANNEL_ID:
        print("CHANNEL_ID missing")
        return

    if not summary:
        text = f"Hello <@{USER_ID}>! No ticket data found."
    else:
        text = (
            f"Hello <@{USER_ID}>! 👋\n\n"
            f"*Ticket Summary by POD*\n\n"
            f"{format_pod_stage_summary(summary)}"
        )

    client.chat_postMessage(channel=CHANNEL_ID, text=text)

if __name__ == "__main__":
    data = fetch_devrev_tickets()
    post_summary(data)
