from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import time
from requests.exceptions import RequestException

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}
pytrends = TrendReq(hl='en-US', tz=360, requests_args={'headers': headers})

def safe_request(pytrends, start, end, max_retries=5):
    timeframe = f"{start.strftime('%Y-%m-%d')} {end.strftime('%Y-%m-%d')}"
    print(f"Fetching data for: {timeframe}")
    
    for attempt in range(max_retries):
        try:
            pytrends.build_payload(kw_list=["Bitcoin"], timeframe=timeframe, geo="US")
            data = pytrends.interest_over_time()

            if not data.empty:
                return data

        except RequestException as e:
            print(f"Fehler bei Anfrage: {e}")
        except Exception as e:
            if "429" in str(e):
                wait_time = (2 ** attempt) * 10  # Exponential Backoff
                print(f"429 Error – warte {wait_time} Sekunden...")
                time.sleep(wait_time)
            else:
                raise e

    print(f"Abfrage für Zeitraum {timeframe} nach {max_retries} Versuchen übersprungen.")
    return pd.DataFrame()  # leeres DataFrame zurückgeben

def daterange(start_date, end_date, step_months=6):
    current = start_date
    while current < end_date:
        next_date = current + pd.DateOffset(months=step_months)
        yield (current, min(next_date, end_date))
        current = next_date

def fetch_bitcoin_trends(start_date_str, end_date_str):
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)
    
    all_data = pd.DataFrame()

    for start, end in daterange(start_date, end_date):
        data = safe_request(pytrends, start, end)
        if not data.empty:
            all_data = pd.concat([all_data, data])
        time.sleep(5)  # zusätzliche kurze Pause zwischen Anfragen

    # Duplikate entfernen, falls vorhanden
    all_data = all_data[~all_data.index.duplicated(keep='first')]

    all_data.to_csv("bitcoin_trends_2015_2025.csv")
    print("CSV exportiert: bitcoin_trends_2015_2025.csv")

# Ausführung
fetch_bitcoin_trends("2023-01-01", "2025-04-01")