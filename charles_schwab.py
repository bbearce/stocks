import os, requests, json
import base64
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID", "NOT FOUND")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "NOT FOUND")
REDIRECT_URI = "https://127.0.0.1"

# Step 1: Generate auth URL
auth_url = (
    "https://api.schwabapi.com/v1/oauth/authorize"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
)

print("Open this URL in your browser:")
print(auth_url)

# Step 2: After approval, paste redirect URL here
redirect_response = input("Paste full redirect URL here:\n")

# Extract code
parsed = urlparse(redirect_response)
code = parse_qs(parsed.query)["code"][0]

# Step 3: Exchange code for token
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

print(token_response.json())
print(token_response.status_code)
print(token_response.text)

tokens = token_response.json()
with open("schwab_tokens.json", "w") as f:
    json.dump(tokens, f)



def refresh_access_token():
    with open("schwab_tokens.json") as f:
        tokens = json.load(f)
    refresh_token = tokens["refresh_token"]
    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()
    response = requests.post(
        "https://api.schwabapi.com/v1/oauth/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    new_tokens = response.json()
    # Preserve refresh token if not returned
    if "refresh_token" not in new_tokens:
        new_tokens["refresh_token"] = refresh_token
    with open("schwab_tokens.json", "w") as f:
        json.dump(new_tokens, f)
    return new_tokens["access_token"]


def get_accounts(access_token):
    response = requests.get(
        "https://api.schwabapi.com/trader/v1/accounts",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    return response.json()



access_token = refresh_access_token()
accounts = get_accounts(access_token)

print(accounts)