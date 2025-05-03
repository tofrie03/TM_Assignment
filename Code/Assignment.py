import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

url = "https://raw.githubusercontent.com/tofrie03/TM_Assignment/refs/heads/main/Material/btc_historical_EUR_2022-01-01_to_2025-04-01_daily.csv"

df = pd.read_csv(url, parse_dates=['Date'], sep=',')

