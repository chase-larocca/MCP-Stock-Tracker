# MCP-Stock-Tracker/discovery/symbol_discovery.py

from yahoo_fin import stock_info as si
import psycopg2
from datetime import datetime
import os
import requests

from db.db_connection import get_connection

def get_trending_symbols():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        quotes = data["finance"]["result"][0]["quotes"]
        return [item["symbol"] for item in quotes][:10]
    except Exception as e:
        print("Error fetching Yahoo trending symbols:", e)
        return []

def update_tracked_symbols(symbols):
    conn = get_connection()
    cursor = conn.cursor()

    for symbol in symbols:
        cursor.execute("""
            INSERT INTO tracked_symbols (symbol, last_seen, active)
            VALUES (%s, %s, TRUE)
            ON CONFLICT (symbol)
            DO UPDATE SET last_seen = EXCLUDED.last_seen, active = TRUE;
        """, (symbol.upper(), datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()

def run_discovery():
    print("[DEBUG] Discovery started")  # Add this line
    symbols = get_trending_symbols()
    print("[DEBUG] Symbols pulled:", symbols)  # Add this line
    if symbols:
        print("Discovered symbols:", symbols)
        update_tracked_symbols(symbols)
    else:
        print("No symbols discovered.")
        

if __name__ == "__main__":
    run_discovery()
