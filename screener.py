# =========================================
# Mini TradingView Screener (Final Version)
# Handles Alpha Vantage Rate Limits
# =========================================

import requests
import pandas as pd
import time
from tabulate import tabulate


# -----------------------------------------
# 1. Fetch Real-Time Stock Data
# -----------------------------------------
def get_realtime_data(symbol, api_key):
    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    )
    response = requests.get(url)
    data = response.json()

    if "Global Quote" in data and data["Global Quote"]:
        return data["Global Quote"]
    else:
        print("\n⛔ Real-time data not available")
        print(data)
        return None


# -----------------------------------------
# 2. Convert Real-Time Data to Table
# -----------------------------------------
def analyze_realtime_data(realtime_data):
    df = pd.DataFrame(realtime_data, index=[0]).T
    df.columns = ["Value"]
    df.index.name = "Metric"
    return df


# -----------------------------------------
# 3. Fetch Historical Stock Data (DAILY)
# -----------------------------------------
def get_historical_data(symbol, api_key):
    url = (
        "https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    )
    response = requests.get(url)
    data = response.json()

    if "Information" in data or "Note" in data:
        print("\n⛔ API RATE LIMIT HIT")
        print(data)
        return None

    if "Time Series (Daily)" in data:
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    else:
        print("\n⛔ Historical data not available")
        print(data)
        return None


# -----------------------------------------
# 4. Calculate Technical Indicators
# -----------------------------------------
def calculate_indicators(df):
    df["MA_50"] = df["4. close"].rolling(50).mean()
    df["MA_200"] = df["4. close"].rolling(200).mean()

    delta = df["4. close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    ema12 = df["4. close"].ewm(span=12, adjust=False).mean()
    ema26 = df["4. close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26

    df.dropna(inplace=True)
    return df


# -----------------------------------------
# 5. Main Program
# -----------------------------------------
def main():
    print("\n📈 MINI TRADINGVIEW SCREENER\n")

    api_key = "267RM5LDHA2ZBGC1"

    symbol = input("Enter stock symbol (Example: AAPL, MSFT, TSLA): ").upper()

    # ---- API CALL 1 ----
    realtime_data = get_realtime_data(symbol, api_key)

    # ⏳ IMPORTANT: wait to avoid rate limit
    time.sleep(15)

    # ---- API CALL 2 ----
    historical_data = get_historical_data(symbol, api_key)

    if realtime_data is None or historical_data is None:
        print("\n❌ Failed to fetch complete stock data.")
        print("👉 Please WAIT 1 minute and try again.")
        return

    realtime_table = analyze_realtime_data(realtime_data)
    indicators = calculate_indicators(historical_data)

    print("\n📌 REAL-TIME STOCK DATA")
    print(tabulate(realtime_table, tablefmt="fancy_grid"))

    print("\n📊 TECHNICAL INDICATORS (LATEST)")
    print(tabulate(indicators.tail(1), headers="keys", tablefmt="fancy_grid"))

    print("\n✅ Analysis Completed Successfully!")


# -----------------------------------------
# 6. Run Program
# -----------------------------------------
if __name__ == "__main__":
    main()
