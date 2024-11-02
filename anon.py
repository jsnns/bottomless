import requests
import logging


def get_instacart_url_from_anon() -> tuple[str, str]:
    url = "https://svc.sandbox.anon.com/account/api/v1/cdpUrl"

    payload = {
        "apps": ["instacart"],
        "appUserId": "sansburyjacob@gmail.com",
        "proxy": False,
    }
    headers = {
        "Authorization": "Bearer anon_Psst/WzqSJTg0gat06QlSgOya+QFfdEST+xa9sXcnIaXK9OrB9ohiTm0H5FmAFYGqfrBOnrrtrRrEHQj",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    url = response.json().get("cdpUrl")

    print("Debug url: ", response.json().get("liveStreamingUrl"))

    if not url:
        logging.error("No cdpUrl found in response")
        return "", ""

    return url, response.json().get("liveStreamingUrl")
