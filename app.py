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

def format_pod_stage_summary(pod_stage_data):
    lines = []

    for pod, pod_data in pod_stage_data.items():
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

def format_pod_account_summary(pod_account_data):
    lines = []

    match_account = {
        "[WMS] Wellness Forever": "Wellness Forever",
        "Wellness Forever": "Wellness Forever",
        "Wellness Forever (TMS)": "Wellness Forever",
        "Wellnessforever": "Wellness Forever",
        "Trancehome linen": "Wellness Forever",
        "Wf": "Wellness Forever",

        "rozana.in": "Rozana",
        "rozanaondemand": "Rozana",
        "rozanaondemanddemo": "Rozana",
        "Freshcarton": "Rozana",
        "FreshCartons": "Rozana",

        "Kimbal": "Kimbal",
        "[WMS] JGH": "JGH",
        "JGH": "JGH",
        "Sugarcosmetics": "Sugarcosmetics",
        "Kama Ayurveda": "Kama Ayurveda",
        "Milkbasket": "Milkbasket",
        "arrowfoods": "arrowfoods",
        "Rubicon": "Rubicon",
        "The Whole Truth": "The Whole Truth",
        "Ripplr": "Ripplr",
        "Superk": "Superk",
        "Spencers": "Spencers",
        "Pramana": "Pramana",
        "Nference": "Nference",
        "Kasha": "Kasha",
        "Meatigo": "Meatigo",
        "Cars24": "Cars24",
        "Incnut": "Incnut",
        "OrangeHealth": "OrangeHealth",
        "Furnishka": "Furnishka",
    }

    for pod, accounts in pod_account_data.items():
        if not accounts:
            continue

        # 🔹 Step 1: Normalize & merge accounts
        merged_accounts = {}

        for raw_account, count in accounts.items():
            canonical_account = match_account.get(raw_account, raw_account)
            merged_accounts[canonical_account] = (
                merged_accounts.get(canonical_account, 0) + count
            )

        # 🔹 Step 2: Output
        lines.append(f"*{pod} — Account Summary*")

        for account, count in sorted(
            merged_accounts.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"    • {account} — {count}")

        lines.append("")

    return "\n".join(lines).strip()

def post_summary(data):
    if not CHANNEL_ID:
        print("CHANNEL_ID missing")
        return

    pod_stage = data.get("pod_stage", {})
    pod_account = data.get("pod_account", {})

    if not pod_stage and not pod_account:
        text = (
            "Hello Team,\n\n"
            "There are currently no active support tickets to report."
        )
    else:
        text = (
            "Hello Team,\n\n"
            "Please find below the latest support ticket summary, \n\n"
            "*📊 Ticket Summary by POD & Stage*\n\n"
            f"{format_pod_stage_summary(pod_stage)}\n\n"
            "*🏢 Ticket Summary by POD & Account*\n\n"
            f"{format_pod_account_summary(pod_account)}\n\n"
            "_This is an automated update generated at regular intervals._"
        )

    client.chat_postMessage(channel=CHANNEL_ID, text=text)

if __name__ == "__main__":
    data = fetch_devrev_tickets()
    post_summary(data)