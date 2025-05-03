import requests
import pandas as pd
import json

url = "https://www.alphavantage.co/query"

params = {
    'function': 'DIGITAL_CURRENCY_DAILY',
    'symbol': 'BTC',
    'market': 'EUR',
    'apikey': 'UD7603KA6BMUN0CK'
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    with open("alpha_vantage_raw_response.json", "w") as f:
        json.dump(data, f, indent=2)
    