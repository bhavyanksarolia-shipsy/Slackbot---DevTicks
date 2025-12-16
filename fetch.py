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