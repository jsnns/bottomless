import requests
import logging


def get_instacart_url_from_anon() -> str:
    url = "https://svc.sandbox.anon.com/account/api/v1/cdpUrl"

    payload = {
        "apps": ["instacart"],
        "appUserId": "sansburyjacob@gmail.com",
        "proxy": True,
    }
    headers = {
        "Authorization": "Bearer anon_Psst/WzqSJTg0gat06QlSgOya+QFfdEST+xa9sXcnIaXK9OrB9ohiTm0H5FmAFYGqfrBOnrrtrRrEHQj",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    live_streaming_url = response.json().get("liveStreamingUrl")

    if not live_streaming_url:
        logging.error("No liveStreamingUrl found in response")
        return ""

    return live_streaming_url
