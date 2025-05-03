import yfinance as yf

start_date = "2012-01-01"
end_date = "2025-04-01"

df = yf.Ticker("BTC-EUR").history(start=start_date, end=end_date, interval="1d")

df.to_csv(f'btc_historical_EUR_{start_date}_to_{end_date}_daily.csv', index=True)