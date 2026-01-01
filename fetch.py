import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEVREV_API_TOKEN = os.getenv("DEVREV_API_TOKEN")

DEVREV_API_URL = "https://api.devrev.ai/works.list"

REQUEST_BODY = {
    "type": "ticket",
    "ticket": {"subtype": "Support"},
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
        "tnt__pod": ["WMS Inbound", "WMS Outbound", "WMS"]
    }
}

REQUEST_HEADERS = {
    "Authorization": f"Bearer {DEVREV_API_TOKEN}",
    "Content-Type": "application/json",
}

def modify_result(results):
    VALID_STAGES = {
        "awaiting_customer_response",
        "queued",
        "awaiting_development",
        "in_development",
        "work_in_progress",
        "Reopen",
        "awaiting_product_assist",
        "Reassigned to Customer Support",
        "resolved",
    }

    VALID_PODS = {"WMS Inbound", "WMS Outbound", "WMS"}

    pod_stage_summary = {}
    pod_account_summary = {}

    for ticket in results.get("works", []):
        pod = ticket.get("custom_fields", {}).get("tnt__pod")
        if pod not in VALID_PODS:
            continue

        stage = ticket.get("stage", {}).get("name")
        if stage not in VALID_STAGES:
            continue

        account_name = (
            ticket.get("account", {}).get("display_name")
            or ticket.get("rev_org", {}).get("display_name")
            or "Unknown Account"
        )

        # POD + STAGE
        pod_stage_summary.setdefault(pod, {"total": 0, "stages": {}})
        pod_stage_summary[pod]["total"] += 1
        pod_stage_summary[pod]["stages"][stage] = (
            pod_stage_summary[pod]["stages"].get(stage, 0) + 1
        )

        # POD + ACCOUNT
        pod_account_summary.setdefault(pod, {})
        pod_account_summary[pod][account_name] = (
            pod_account_summary[pod].get(account_name, 0) + 1
        )

    return {
        "pod_stage": pod_stage_summary,
        "pod_account": pod_account_summary,
    }

def fetch_devrev_tickets():
    response = requests.post(
        DEVREV_API_URL,
        headers=REQUEST_HEADERS,
        json=REQUEST_BODY,
        timeout=15,
    )
    response.raise_for_status()

    return modify_result(response.json())