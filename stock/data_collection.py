import yfinance as yf
import pandas as pd
company_list=[{"symbol":"INFY.NS","name":"Infosys Limited"},{"symbol":"TCS.NS","name":"Tata Consultancy Services Limited"},{"symbol":"HDFCBANK.NS","name":"HDFC Bank Limited"},]
def get_company_ticker(company_name):
    for company in company_list:
        if company["name"] == company_name:
            return company["symbol"]
    return None


def get_historicaldata(ticker,period="1y",interval="1d"):
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
    df=get_historicaldata(yf.Ticker(symbol))
    df=calculate_technical_indicators(df)
    return df

def main():
    company_name=input("Enter the company name: ")
    ticker_symbol=get_company_ticker(company_name)
    ticker=yf.Ticker(ticker_symbol)
    df=get_historicaldata(ticker)
    df=calculate_technical_indicators(df)
    print(df.tail(60))
if __name__ == "__main__":
    main()    