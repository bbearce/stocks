# schwab_login.py

import os
import json
import base64
import requests
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://127.0.0.1"

def main():
    auth_url = (
        "https://api.schwabapi.com/v1/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    print("\nOpen this URL in your browser:\n")
    print(auth_url)

    redirect_response = input("\nPaste full redirect URL here:\n")

    parsed = urlparse(redirect_response)
    code = parse_qs(parsed.query)["code"][0]

    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    token_response = requests.post(
        "https://api.schwabapi.com/v1/oauth/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }
    )

    tokens = token_response.json()

    if token_response.status_code != 200:
        print("Error:")
        print(token_response.text)
        return

    with open("schwab_tokens.json", "w") as f:
        json.dump(tokens, f, indent=2)

    print("\nTokens saved to schwab_tokens.json")
    print("You do not need to run this again unless refresh token expires.\n")

if __name__ == "__main__":
    main()
