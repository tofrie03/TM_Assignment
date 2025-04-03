import yfinance as yf

df = yf.Ticker("BTC-EUR").history(period="5y")

df.to_csv('btc_historical_EUR.csv', index=True)