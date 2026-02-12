# schwab_client.py

import os, pdb
import json
import base64
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TOKEN_FILE = "schwab_tokens.json"

TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
BASE_URL = "https://api.schwabapi.com/trader/v1"

def _auth_header():
    return base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

def refresh_access_token():
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    refresh_token = tokens["refresh_token"]

    response = requests.post(
        TOKEN_URL,
        headers={
            "Authorization": f"Basic {_auth_header()}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )

    new_tokens = response.json()

    if response.status_code != 200:
        raise Exception(f"Refresh failed: {response.text}")

    if "refresh_token" not in new_tokens:
        new_tokens["refresh_token"] = refresh_token

    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f, indent=2)

    return new_tokens["access_token"]

def get_accounts():
    access_token = refresh_access_token()

    response = requests.get(
        f"{BASE_URL}/accounts",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def get_account_hash_value(accountNumber):
    access_token = refresh_access_token()

    response = requests.get(
        f"{BASE_URL}/accounts/accountNumbers",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    accounts = response.json()
    for account in accounts:
        if account['accountNumber'] == accountNumber:
            hashValue = account['hashValue']
    return hashValue


def get_positions(account_hash):
    access_token = refresh_access_token()
    # pdb.set_trace()
    response = requests.get(
        f"{BASE_URL}/accounts/{account_hash}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params={
            "fields": "positions"
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    securities = data.get("securitiesAccount", {})
    positions = securities.get("positions", [])

    return positions



def get_positions_df(account_hash):
    raw_positions = get_positions(account_hash)

    rows = []

    for pos in raw_positions:
        instrument = pos.get("instrument", {})

        rows.append({
            "symbol": instrument.get("symbol"),
            "description": instrument.get("description"),
            "asset_type": instrument.get("assetType"),
            "quantity": pos.get("longQuantity", 0),
            "cost_basis": pos.get("averagePrice"),
            "market_value": pos.get("marketValue"),
        })

    return pd.DataFrame(rows)


