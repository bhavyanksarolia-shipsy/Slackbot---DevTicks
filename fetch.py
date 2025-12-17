import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEVREV_API_TOKEN = os.getenv("DEVREV_API_TOKEN")

DEVREV_API_URL = "https://api.devrev.ai/works.list"

REQUEST_BODY = {
    "type": "ticket",
    "ticket": {
        "subtype": "Support"
    },
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
        "tnt__pod": ["WMS Inbound","WMS Outbound","WMS"]
    }
}

REQUEST_HEADERS = {
    "Authorization": f"Bearer {DEVREV_API_TOKEN}",
    "Content-Type": "application/json",
}

def format_pod_stage_summary(data):
    lines = []

    for pod, pod_data in data.items():
        total = pod_data["total"]

        # Skip empty pods (optional, but cleaner)
        if total == 0:
            continue

        # POD heading
        lines.append(f"*{pod}* ({total})")

        # Stage breakdown
        for stage, count in pod_data["stages"].items():
            readable_stage = stage.replace("_", " ").title()
            lines.append(f"    • {readable_stage} — {count}")

        # Blank line between pods
        lines.append("")

    return "\n".join(lines).strip()


def modify_result(results):
    VALID_STAGES = [
        "awaiting_customer_response",
        "queued",
        "awaiting_development",
        "in_development",
        "work_in_progress",
        "Reopen",
        "awaiting_product_assist",
        "Reassigned to Customer Support",
    ]

    VALID_PODS = ["WMS Inbound", "WMS Outbound", "WMS"]

    output = {}

    for ticket in results.get("works", []):

        pod = ticket.get("custom_fields", {}).get("tnt__pod")
        if pod not in VALID_PODS:
            pod = "none"

        # Initialize POD bucket if needed
        if pod not in output:
            output[pod] = {
                "total": 0,
                "stages": {}
            }

        stage = ticket.get("stage", {}).get("name")
        if stage not in VALID_STAGES:
            stage = "none"

        output[pod]["total"] += 1
        output[pod]["stages"][stage] = (
            output[pod]["stages"].get(stage, 0) + 1
        )

    return output


def fetch_devrev_tickets():
    response = requests.post(
        DEVREV_API_URL,
        headers=REQUEST_HEADERS,
        json=REQUEST_BODY
    )
    response.raise_for_status()

    aggregated = modify_result(response.json())
    return aggregated