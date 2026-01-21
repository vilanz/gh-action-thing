import json
import hmac
import hashlib
from os import environ
from datetime import datetime, timezone

import requests

def create_json_payload(name, email, resume_link, repository_link, action_run_link):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "email": email,
        "resume_link": resume_link,
        "repository_link": repository_link,
        "action_run_link": action_run_link
    }
    json_body = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return json_body

def create_hmac_sha_256_signature(json_body, secret):
    signature = hmac.new(
        secret.encode('utf-8'),
        json_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def post_to_b12_endpoint(json_body, signature):
    url = environ["PAYLOAD_TARGET_URL"]
    headers = {
        "X-Signature-256": signature,
        "Content-Type": "application/json"
    }
    print(headers, json_body)
    response = requests.post(url, data=json_body, headers=headers)
    return response

def main():
    name = environ["PAYLOAD_NAME"]
    email = environ["PAYLOAD_EMAIL"]
    resume_link = environ["PAYLOAD_RESUME_LINK"]
    repository_link = environ["PAYLOAD_REPOSITORY_LINK"]
    action_run_link = f"{repository_link}/actions/runs/{environ["GITHUB_RUN_ID"]}"
    json_body = create_json_payload(name, email, resume_link, repository_link, action_run_link)

    secret = environ["PAYLOAD_WEBHOOK_SECRET"]
    signature = create_hmac_sha_256_signature(json_body, secret)

    response = post_to_b12_endpoint(json_body, signature)

    if response.status_code == 200:
        receipt = response.json()['receipt']
        print(f"Success! Receipt: {receipt}")
    else:
        print(f"Failed! Response code was {response.status_code}")
        print(response)
        print(response.text)

if __name__ == "__main__":
    main()
