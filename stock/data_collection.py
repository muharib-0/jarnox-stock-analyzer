import yfinance as yf
import math
import numpy as np

# --------------------
# In-memory cache
# --------------------
_cache = {}

# --------------------
# Company list
# --------------------
company_list = [
    {"symbol": "INFY.NS", "name": "Infosys Limited"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited"},
]

# --------------------
# Timeframe mapping
# --------------------
TIMEFRAME_MAP = {
    "30d": ("1mo", "1d"),
    "90d": ("3mo", "1d"),
    "6mo": ("6mo", "1d"),
    "1y": ("1y", "1d"),
}

# --------------------
# Helpers
# --------------------
import math

def safe_float(value):
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return float(value)



# --------------------
# Data fetching
# --------------------
def get_historicaldata(ticker, timeframe="30d"):
    if timeframe not in TIMEFRAME_MAP:
        raise ValueError("Invalid timeframe")

    period, interval = TIMEFRAME_MAP[timeframe]
    try:
        df = ticker.history(period=period, interval=interval)
        if df is None or df.empty:
            return None
        return df
    except Exception:
        return None


# --------------------
# Indicators
# --------------------
def calculate_technical_indicators(df):
    df = df.copy()

    df["daily_return"] = (df["Close"] - df["Open"]) / df["Open"]
    df["moving_average_7"] = df["Close"].rolling(window=7).mean()
    df["volatility_30"] = df["daily_return"].rolling(window=30).std() * 100

    # 52-week indicators only make sense if we have enough data
    if len(df) >= 252:
        df["_52_week_high"] = df["High"].rolling(window=252).max()
        df["_52_week_low"] = df["Low"].rolling(window=252).min()
    else:
        df["_52_week_high"] = None
        df["_52_week_low"] = None

    return df


# --------------------
# Analysis pipeline
# --------------------
def analyze_stock(symbol, timeframe="30d"):
    cache_key = f"{symbol}:{timeframe}"

    if cache_key in _cache:
        return _cache[cache_key]

    df = get_historicaldata(yf.Ticker(symbol), timeframe)
    if df is None or df.empty:
        return None

    df = calculate_technical_indicators(df)
    _cache[cache_key] = df
    return df


# --------------------
# Summary builder
# --------------------
def build_summary(df, symbol: str) -> dict:
    latest = df.iloc[-1]

    close = safe_float(latest.get("Close"))
    ma7 = safe_float(latest.get("moving_average_7"))
    vol = safe_float(latest.get("volatility_30"))
    high_52 = safe_float(latest.get("_52_week_high"))
    low_52 = safe_float(latest.get("_52_week_low"))

    short_term_trend = (
        "up" if ma7 is not None and close is not None and close > ma7 else "down"
    )

    volatility_label = (
        None if vol is None else
        "Low" if vol < 1 else
        "Moderate" if vol < 2 else
        "High"
    )

    position_52w = None
    if (
        close is not None
        and high_52 is not None
        and low_52 is not None
        and high_52 != low_52
    ):
        position_52w = round((close - low_52) / (high_52 - low_52) * 100, 2)

    return {
        "symbol": symbol,
        "latest_date": latest.name.date().isoformat(),
        "latest_close": round(close, 2) if close is not None else None,
        "short_term_trend": short_term_trend,
        "volatility": {
            "value_percent": round(vol, 2) if vol is not None else None,
            "label": volatility_label,
        },
        "position_in_52_week_range_percent": position_52w,
    }



# --------------------
# Comparison
# --------------------
def compare_summaries(summary1: dict, summary2: dict) -> dict:
    symbol1 = summary1["symbol"]
    symbol2 = summary2["symbol"]

    vol1 = summary1["volatility"]["value_percent"]
    vol2 = summary2["volatility"]["value_percent"]

    pos1 = summary1["position_in_52_week_range_percent"]
    pos2 = summary2["position_in_52_week_range_percent"]

    more_volatile = None
    if vol1 is not None and vol2 is not None:
        if vol1 > vol2:
            more_volatile = symbol1
        elif vol2 > vol1:
            more_volatile = symbol2

    closer_to_52_week_high = None
    if pos1 is not None and pos2 is not None:
        if pos1 > pos2:
            closer_to_52_week_high = symbol1
        elif pos2 > pos1:
            closer_to_52_week_high = symbol2

    return {
        "more_volatile": more_volatile,
        "closer_to_52_week_high": closer_to_52_week_high,
        "trend_comparison": {
            symbol1: summary1["short_term_trend"],
            symbol2: summary2["short_term_trend"],
        },
    }
