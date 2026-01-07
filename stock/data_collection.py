import yfinance as yf



_cache={}

company_list=[{"symbol":"INFY.NS","name":"Infosys Limited"},{"symbol":"TCS.NS","name":"Tata Consultancy Services Limited"},{"symbol":"HDFCBANK.NS","name":"HDFC Bank Limited"},]




def get_historicaldata(symbol,period="1y",interval="1d"):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)
    return hist



def calculate_technical_indicators(df):
     df['daily_return']=(df['Close']-df['Open'])/df['Open']
     df['moving_average_7']=df['Close'].rolling(window=7).mean()
     df['_52_week_high']=df['High'].rolling(window=252).max()
     df['_52_week_low']=df['Low'].rolling(window=252).min()
     df['volatility_30']=df['daily_return'].rolling(window=30).std()*100
     return df


def analyze_stock(symbol):
    if symbol in _cache:
        return _cache[symbol]

    df = get_historicaldata(symbol)
    if df.empty:
        return None

    df = calculate_technical_indicators(df)
    _cache[symbol] = df
    return df


def build_summary(df, symbol: str) -> dict:
    latest = df.iloc[-1]

    close = float(latest["Close"])
    ma7 = latest.get("moving_average_7")
    vol = latest.get("volatility_30")
    high_52 = latest.get("_52_week_high")
    low_52 = latest.get("_52_week_low")

    # short-term trend
    short_term_trend = (
        "up" if ma7 is not None and close > ma7 else "down"
    )

    # volatility label
    volatility_label = (
        None if vol is None else
        "Low" if vol < 1 else
        "Moderate" if vol < 2 else
        "High"
    )

    # 52-week position
    position_52w = (
        round((close - low_52) / (high_52 - low_52) * 100, 2)
        if high_52 and low_52 and high_52 != low_52
        else None
    )

    return {
        "symbol": symbol,
        "latest_date": latest.name.date().isoformat(),
        "latest_close": round(close, 2),
        "short_term_trend": short_term_trend,
        "volatility": {
            "value_percent": round(vol, 2) if vol is not None else None,
            "label": volatility_label,
        },
        "position_in_52_week_range_percent": position_52w,
    }

