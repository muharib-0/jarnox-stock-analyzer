
import yfinance as yf
import pandas as pd
Infosys = yf.Ticker("INFY.NS")
def get_historicaldata(period="1y",interval="1d"):
    hist = Infosys.history(period=period, interval=interval)
    return hist
df=get_historicaldata()
# print(df.head(20))
# print(df.tail(20))
# print(df.info())
# df_new=df.assign(Daily_Return=lambda x:(x['Close']-x['Open'])/x['Open'])
# print(df_new.head(20))
df['daily_return']=(df['Close']-df['Open'])/df['Open']
# print(df.head(20))
df['moving_average_7']=df['Close'].rolling(window=7).mean()
# for i in range(len(df)):
#     if i<6:
#         df.loc[df.index[i],'moving_average_7']=None
#     else:
#         df.loc[df.index[i],'moving_average_7']=df['Close'][i-6:i+1].mean()
# # print(df.head(20))
df['_52_week_high']=df['Close'].rolling(window=252).max()
df['_52_week_low']=df['Close'].rolling(window=252).min()
# for i in range(len(df)):
#     if i<251:
#         df.loc[df.index[i],'_52_week_high']=None
#     else:
#         df.loc[df.index[i],'_52_week_high']=df['Close'][i-251:i+1].max()
# # df['_52_week_high']=df['Close'].rolling(window=252).max()
# for i in range(len(df)):
#     if i<251:
#         df.loc[df.index[i],'_52_week_low']=None
#     else:
#         df.loc[df.index[i],'_52_week_low']=df['Close'][i-251:i+1].min()
df['volatility_30']=df['daily_return'].rolling(window=30).std()*100
print(df.tail(60))