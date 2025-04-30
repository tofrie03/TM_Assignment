import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

url = "https://raw.githubusercontent.com/tofrie03/TM_Assignment/refs/heads/main/Material/btc_historical_EUR_3y.csv"

df = pd.read_csv(url, parse_dates=['Date'], sep=',')

print(df.head())