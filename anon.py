import requests
import logging
import os
from dotenv import load_dotenv
import time

load_dotenv()  # Add this to load .env file

def get_instacart_url_from_anon() -> tuple[str, str]:
    url = "https://svc.sandbox.anon.com/account/api/v1/cdpUrl"

    payload = {
        "apps": ["instacart"],
        "appUserId": os.getenv("ANON_APP_USER_ID"),
        "proxy": False,
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('ANON_API_KEY')}",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    url = response.json().get("cdpUrl")

    print("Debug url: ", response.json().get("liveStreamingUrl"))
    print("Waiting 7 seconds for you to open the url in your browser, in case you'd like to follow along")
    time.sleep(7)

    if not url:
        logging.error("No cdpUrl found in response")
        return "", ""

    return url, response.json().get("liveStreamingUrl")
