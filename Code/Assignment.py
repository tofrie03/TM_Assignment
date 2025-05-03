# --- 1. Konfiguration & Imports ---
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
from IPython.display import display

api_cunef = "UD7603KA6BMUN0CK"
api_cbs = "3JZJXQFD2F0K85IT"

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)
pd.set_option('display.float_format', '{:.2f}'.format)

# --- 2. Daten laden ---
url = "https://media.githubusercontent.com/media/tofrie03/TM_Assignment/refs/heads/main/Material/btc_historical_EUR_2015-01-01_to_2025-03-01_daily.csv"
df_historical = pd.read_csv(url, sep=',')
df_historical['Date'] = pd.to_datetime(df_historical['Date']).dt.strftime('%Y-%m-%d')
df_historical['Date'] = pd.to_datetime(df_historical['Date'])
df_historical.sort_values('Date', inplace=True)

print(df_historical.head())

# --- 2.1. Daten von Alpha Vantage ---
url = "https://www.alphavantage.co/query"
params = {
    'function': 'DIGITAL_CURRENCY_DAILY',
    'symbol': 'BTC',
    'market': 'EUR',
    'apikey': api_cbs
}
response = requests.get(url, params=params)

start_date = (df_historical['Date'].max() + pd.Timedelta(days=1)).date().isoformat()
today = pd.to_datetime("today").strftime("%Y-%m-%d")

if response.status_code == 200:
    data = response.json()
    df_new = pd.DataFrame.from_dict(
        data["Time Series (Digital Currency Daily)"],
        orient='index'
    ).reset_index()

    df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df_new['Date'] = pd.to_datetime(df_new['Date']).dt.strftime('%Y-%m-%d')
    df_new['Date'] = pd.to_datetime(df_new['Date'])
    print(df_new.head())
    df_new.sort_values('Date', inplace=True)

    # Filter for dates greater than the last date in the historical data
    df_new = df_new[df_new['Date'] >= pd.to_datetime(start_date)]
    df_new.reset_index(drop=True, inplace=True)

    # Handelsvolumen in EUR berechnen (Volume in BTC × durchschnittlicher Tagespreis in EUR)
    df_new[['Open', 'High', 'Low', 'Close']] = df_new[['Open', 'High', 'Low', 'Close']].astype(float)
    df_new['AvgPrice'] = df_new[['Open', 'High', 'Low', 'Close']].mean(axis=1)
    df_new['Volume'] = df_new['Volume'].astype(float)
    df_new['Volume'] = df_new['Volume'] * df_new['AvgPrice']
    df_new.drop(columns=['AvgPrice'], inplace=True)

    print(df_new.head())

    # Historische und neue Daten zusammenführen
    df = pd.concat([df_historical, df_new], ignore_index=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
else:
    print("Fehler beim Abrufen der Daten von Alpha Vantage:", response.status_code)

print(df.tail(200))

# --- 3. Data Cleaning ---

# Numerische Spalten einheitlich auf 2 Nachkommastellen runden
float_cols = df.select_dtypes(include='float').columns
df[float_cols] = df[float_cols].round(2)

# Volume-Spalte explizit in float konvertieren und auf 2 Nachkommastellen runden
df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').round(2)

print(df.tail(200))

# Datentypen prüfen
print("Datentypen der Spalten:")
print(df.dtypes)

# Fehlende Werte anzeigen
print("Fehlende Werte pro Spalte:")
print(df.isna().sum())

# Doppelte Einträge prüfen
print("\nDoppelte Zeilen:", df.duplicated().sum())

# Ungültige Werte prüfen
invalid_rows = df[(df['Low'] > df['High']) | (df['Open'] > df['High']) | (df['Close'] > df['High'])]
print("\nUngültige Zeilen (z.B. Low > High):", len(invalid_rows))
print(invalid_rows)

# Zeitstempel formatieren & sortieren
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.sort_values('Date')

# Zeitlücken prüfen
df_indexed = df.set_index('Date')
date_range = pd.date_range(start=df_indexed.index.min(), end=df_indexed.index.max(), freq='D')
missing_dates = date_range.difference(df_indexed.index)
print("\nFehlende Datenpunkte:", len(missing_dates))

# Visualisierung fehlender Werte
missing_values = df.isna().sum()
missing_values = missing_values[missing_values > 0]
if not missing_values.empty:
    missing_values.plot(kind='bar', title='Fehlende Werte pro Spalte')
    plt.ylabel('Anzahl fehlender Werte')
    plt.show()

# Zeitreihe der Close-Werte
plt.figure(figsize=(12, 4))
plt.plot(df['Date'], df['Close'])
plt.title('Bitcoin-Schlusskurs über Zeit')
plt.xlabel('Datum')
plt.ylabel('Close')
plt.grid(True)
plt.tight_layout()
plt.show()

# Zeitreihe des Volumens
plt.figure(figsize=(12, 4))
plt.plot(df['Date'], df['Volume'])
plt.title('Bitcoin-Handelsvolumen über Zeit')
plt.xlabel('Datum')
plt.ylabel('Volumen')
plt.grid(True)
plt.tight_layout()
plt.show()

# Ungültige Zeilen anzeigen
if not invalid_rows.empty:
    print("\nUngültige Zeilen-Vorschau:")
    display(invalid_rows.head())

# --- 4. Korrektur unplausibler Volumenwerte ---
volume_mask = df["Volume"] > 200_000_000_000
for idx in df[volume_mask].index:
    prev_volume = df.at[idx - 1, "Volume"]
    next_volume = df.at[idx + 1, "Volume"]
    df.at[idx, "Volume"] = (prev_volume + next_volume) / 2

# --- 5. Visualisierung aller numerischen Spalten ---
numeric_cols = df.select_dtypes(include='number').columns
numeric_cols = [col for col in numeric_cols if df[col].nunique() > 1]
num_cols = len(numeric_cols)

fig, axes = plt.subplots(num_cols, 1, figsize=(12, 2.5 * num_cols), sharex=True)

for i, col in enumerate(numeric_cols):
    ax = axes[i]
    ax.plot(df['Date'], df[col], label=col)
    ax.ticklabel_format(style='plain', axis='y')
    ax.set_ylabel(col)
    ax.legend(loc='upper right')
    ax.grid(True)

axes[0].set_title('Numerische Spalten als Zeitreihe')
axes[-1].set_xlabel('Datum')
plt.tight_layout()
plt.show()