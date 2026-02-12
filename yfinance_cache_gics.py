import yfinance as yf
import time
import pandas as pd

def build_sector_lookup(symbols):
    rows = []
    for sym in symbols:
        try:
            info = yf.Ticker(sym).info
            rows.append({
                "symbol": sym,
                "sector": info.get("sector"),
                "industry": info.get("industry")
            })
        except:
            rows.append({
                "symbol": sym,
                "sector": None,
                "industry": None
            })
        time.sleep(2)  # avoid rate limit
    return pd.DataFrame(rows)


current_positions = pd.read_csv("Individual-Positions-2024-06-20-160845.csv")

sector_lookup = build_sector_lookup(current_positions["symbol"].unique()[0:2])
sector_lookup.to_csv("sector_lookup.csv", index=False)
