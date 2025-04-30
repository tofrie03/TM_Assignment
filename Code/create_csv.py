import yfinance as yf

period = 3

df = yf.Ticker("BTC-EUR").history(period=f"{period}y")

df.to_csv(f'btc_historical_EUR_{period}y.csv', index=True)