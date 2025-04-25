import os
import json
import sqlite3
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# config
load_dotenv()
CMC_API_KEY = os.getenv("CMC_API_KEY")
CONFIG_FILE = "config.json"
DB_FILE = "portfolio.db"


def init_db():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            symbol TEXT,
            amount REAL,
            price REAL,
            value REAL,
            price_change REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            total_value REAL,
            currency TEXT,
            value_change REAL
        )
    """)

    conn.commit()
    conn.close()


def load_config():

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config["portfolio"], config["currency"]
    except Exception as e:
        print(f"Config load error: {e}")
        return None, None


def get_cmc_data(api_key, symbols, currency):

    # get quotes
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": api_key}
    params = {"symbol": ",".join(symbols), "convert": currency}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data["data"] if response.status_code == 200 else None
    except Exception as e:
        print(f"API Error: {e}")
        return None


def get_previous():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT total_value FROM portfolio_history 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def get_previous_prices(symbol):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT price FROM tokens 
        WHERE symbol = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (symbol,))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def save_to_db(tokens_data, total_value, currency, value_change ):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for token in tokens_data:
        cursor.execute("""
            INSERT INTO tokens (timestamp, symbol, amount, price, value, price_change )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            token["symbol"],
            token["amount"],
            token["price"],
            token["value"],
            token["price_change "]
        ))

    cursor.execute("""
        INSERT INTO portfolio_history (timestamp, total_value, currency, value_change )
        VALUES (?, ?, ?, ?)
    """, (timestamp, total_value, currency, value_change ))

    conn.commit()
    conn.close()


def display_portfolio(data, total, currency, total_change ):

    print("\n" + "-" * 70)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Update")
    print("-" * 70)

    for item in data:
        change  = item["price_change "]
        if change  is not None:
            change_str = f" | Change: {change :+.2f}%"
        else:
            change_str = " | Change: N/A"

        print(
            f"{item['symbol']}: {item['amount']}  | "
            f"Price: {item['price']} {currency} | "
            f"Value: {item['value']} {currency}"
            f"{change_str}"
        )

    print("-" * 70)

    if total_change  is not None:
        change_str = f" ({total_change :+.2f}%)"
    else:
        change_str = ""

    print(f"TOTAL: {total} {currency}{change_str}\n")


def main():
    init_db()

    while True:
        portfolio, currency = load_config()
        if not portfolio:
            print("Token list not loaded. Check config.json.")
            time.sleep(300)
            continue

        cmc_data = get_cmc_data(CMC_API_KEY, portfolio.keys(), currency)
        if not cmc_data:
            print("ERROR API. Retry in 5 min...")
            time.sleep(300)
            continue

        tokens_data = []
        total_value = 0

        for symbol, amount in portfolio.items():
            if symbol not in cmc_data:
                print(f"Token {symbol} not found!")
                continue

            price = cmc_data[symbol]["quote"][currency]["price"]
            value = price * amount

            # token changes count
            previous_price = get_previous_prices(symbol)
            if previous_price and previous_price != 0:
                price_change  = ((price - previous_price) / previous_price) * 100
            else:
                price_change  = None

            tokens_data.append({
                "symbol": symbol,
                "amount": amount,
                "price": round(price, 4),
                "value": round(value, 2),
                "price_change ": round(price_change , 2) if price_change  is not None else None
            })
            total_value += value

        total_value = round(total_value, 2)

        # total changes count
        previous_total = get_previous()
        if previous_total and previous_total != 0:
            total_change  = ((total_value - previous_total) / previous_total) * 100
        else:
            total_change  = None

        # saving
        save_to_db(tokens_data, total_value, currency,
                   round(total_change , 2) if total_change  is not None else None)
        display_portfolio(tokens_data, total_value, currency,
                          total_change  if total_change  is not None else None)

        time.sleep(300)  # 5 min update


if __name__ == "__main__":
    main()