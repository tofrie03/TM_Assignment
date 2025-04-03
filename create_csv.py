import yfinance as yf

df = yf.Ticker("BTC-EUR").history(period="10y")

df.to_csv('btc_historical_EUR_10y.csv', index=True)