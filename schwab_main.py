import os
from schwab_client import get_accounts, get_account_hash_value, get_positions_df
import pprint
from dotenv import load_dotenv

load_dotenv()

accounts = get_accounts()
# pprint.pprint(accounts) # debug

IRA_ACCOUNT_NUMBER = os.getenv("IRA_ACCOUNT_NUMBER")
ROTH_ACCOUNT_NUMBER = os.getenv("ROTH_ACCOUNT_NUMBER")
BROKERAGE_ACCOUNT_NUMBER = os.getenv("BROKERAGE_ACCOUNT_NUMBER")


account_map = {}
for acct in accounts:
    acct_info = acct["securitiesAccount"]
    account_number = acct_info["accountNumber"]
    account_type = acct_info["type"]
    account_hash = get_account_hash_value(account_number)
    account_map[account_number] = {
        "number": account_number,
        "hash": account_hash
    }

print(account_map)


account_ira_hash = get_account_hash_value(IRA_ACCOUNT_NUMBER)
account_roth_hash = get_account_hash_value(ROTH_ACCOUNT_NUMBER)
account_brokerage_hash = get_account_hash_value(BROKERAGE_ACCOUNT_NUMBER)


positions_roth_df = get_positions_df(account_roth_hash)
positions_ira_df = get_positions_df(account_ira_hash)
positions_brokerage_df = get_positions_df(account_brokerage_hash)

