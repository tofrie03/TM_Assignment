# --- 1. Configuration & Imports ---
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import matplotlib.ticker as mat_ticker
from IPython.display import display
import yfinance as yf

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)
pd.set_option('display.float_format', '{:.2f}'.format)

api_works = False

# --- 2. Load data ---
# Load historical Bitcoin data from GitHub
url = "https://media.githubusercontent.com/media/tofrie03/TM_Assignment/refs/heads/main/Material/btc_historical_EUR_2015-01-01_to_2025-03-01_daily.csv"
df_historical = pd.read_csv(url, sep=',')
df_historical['Date'] = pd.to_datetime(df_historical['Date']).dt.strftime('%Y-%m-%d')
df_historical['Date'] = pd.to_datetime(df_historical['Date'])
df_historical.sort_values('Date', inplace=True)

# --- 2.1. Data from Alpha Vantage ---
# Load API data or use simulated response
if api_works:
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'DIGITAL_CURRENCY_DAILY',
        'symbol': 'BTC',
        'market': 'EUR',
        'apikey': 'UD7603KA6BMUN0CK'
    }
    response = requests.get(url, params=params)
else:
    # Simulated API response in case the API does not work
    url = "https://raw.githubusercontent.com/tofrie03/TM_Assignment/refs/heads/main/Material/alphavantage_raw_response.json"
    response = requests.get(url)

data = response.json()

df_new = pd.DataFrame.from_dict(
    data["Time Series (Digital Currency Daily)"],
    orient='index'
).reset_index()

df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
df_new['Date'] = pd.to_datetime(df_new['Date']).dt.strftime('%Y-%m-%d')
df_new['Date'] = pd.to_datetime(df_new['Date'])
df_new.sort_values('Date', inplace=True)

# Determine the start date for new data based on the last historical date
start_date = (df_historical['Date'].max() + pd.Timedelta(days=1)).date().isoformat()

# Filter for data from the start date
df_new = df_new[df_new['Date'] >= pd.to_datetime(start_date)]
df_new.reset_index(drop=True, inplace=True)

# Merge historical and new data
df = pd.concat([df_historical, df_new], ignore_index=True)
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)
df.reset_index(drop=True, inplace=True)


# --- 3. Data Cleaning ---

# Display first and last rows of the DataFrame
print(df.head())
print(df.tail())

# Check data types of columns
print("Data types of columns:")
print(df.dtypes)

# Ensure OHLC columns are numeric
df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].apply(pd.to_numeric, errors='coerce')

# Round numeric columns to 2 decimal places
float_cols = df.select_dtypes(include='float').columns
df[float_cols] = df[float_cols].round(2)

# --- Replace volume from yfinance for the entire date range ---
start = df['Date'].min().strftime('%Y-%m-%d')
end = (df['Date'].max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

# Load trading volume from yfinance
yf_df = yf.Ticker('BTC-EUR').history(start=start, end=end, interval='1d')
yf_df.reset_index(inplace=True)
yf_df = yf_df[['Date', 'Volume']]

# Remove original Volume column and replace with yfinance data
df.drop(columns='Volume', inplace=True)
yf_df['Date'] = pd.to_datetime(yf_df['Date']).dt.strftime('%Y-%m-%d')
yf_df['Date'] = pd.to_datetime(yf_df['Date'])
yf_df.sort_values('Date', inplace=True)
yf_df.reset_index(drop=True, inplace=True)
df = pd.merge(df, yf_df, on='Date', how='left')

# Display missing values per column
print("Missing values per column:")
print(df.isna().sum())

# Output value range of Dividends and Stock Splits columns
print("\nValue range Dividends:")
print(df['Dividends'].describe())
print("\nValue range Stock Splits:")
print(df['Stock Splits'].describe())

# Visualization of Dividends and Stock Splits over time
fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

df.plot(x='Date', y='Dividends', ax=ax[0], title='Dividends over time', legend=False)
ax[0].set_ylabel('Dividends')

df.plot(x='Date', y='Stock Splits', ax=ax[1], title='Stock Splits over time', legend=False)
ax[1].set_ylabel('Stock Splits')

plt.xlabel('Date')
plt.tight_layout()
plt.show()

# Remove Dividends and Stock Splits as they are not needed
df.drop(columns=['Dividends', 'Stock Splits'], inplace=True)

# Check and output duplicate entries
print("\nDuplicate rows:", df.duplicated().sum())

if df.duplicated().sum() > 0:
    df.drop_duplicates(inplace=True)

# Check for invalid values in OHLC columns
invalid_rows = df[(df['Low'] > df['High']) | (df['Open'] > df['High']) | (df['Close'] > df['High']) | (df['Open'] < df['Low']) | (df['Close'] < df['Low'])]
print("\nInvalid rows:", len(invalid_rows))
print(invalid_rows)

# Correct faulty High values: High = max(Open, Close, Low, High)
for idx in invalid_rows.index:
    row = df.loc[idx, ['Open', 'Close', 'Low', 'High']]
    max_val = row.max()
    if max_val > df.at[idx, 'High']:
        df.at[idx, 'High'] = max_val

# Correct faulty Low values: Low = min(Open, Close, Low, High)
for idx in invalid_rows.index:
    row = df.loc[idx, ['Open', 'Close', 'Low', 'High']]
    min_val = row.min()
    if min_val < df.at[idx, 'Low']:
        df.at[idx, 'Low'] = min_val

# Check for time gaps to see if all days are present
df_indexed = df.set_index('Date')
date_range = pd.date_range(start=df_indexed.index.min(), end=df_indexed.index.max(), freq='D')
missing_dates = date_range.difference(df_indexed.index)
print("\nMissing data points:", len(missing_dates))

# Plot time series of volume
plt.figure(figsize=(12, 4))
plt.plot(df['Date'], df['Volume'])
plt.title('Bitcoin trading volume over time')
plt.xlabel('Date')
plt.ylabel('Volume')
plt.grid(True)
plt.gca().yaxis.set_major_formatter(mat_ticker.StrMethodFormatter('{x:,.0f}'))
plt.tight_layout()
plt.show()

# Identify volume values that are unrealistically high and correct them by averaging neighbors
volume_mask = df["Volume"] > 150_000_000_000
for idx in df[volume_mask].index:
    prev_volume = df.at[idx - 1, "Volume"]
    next_volume = df.at[idx + 1, "Volume"]
    df.at[idx, "Volume"] = (prev_volume + next_volume) / 2

# Visualization of all numeric columns
numeric_cols = df.select_dtypes(include='number').columns
numeric_cols = [col for col in numeric_cols if df[col].nunique() > 1]

fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(12, 2.5 * len(numeric_cols)), sharex=True)

for i, col in enumerate(numeric_cols):
    ax = axes[i]
    ax.plot(df['Date'], df[col], label=col)
    ax.ticklabel_format(style='plain', axis='y')
    ax.set_ylabel(col)
    ax.legend(loc='upper right')
    ax.grid(True)

axes[0].set_title('Numeric columns as time series')
axes[-1].set_xlabel('Date')
plt.tight_layout()
plt.show()


# --- 6. Machine Learning: Predict price increase based on sentiment + volume ---

# Step 1: Create target variable (price increase next day)
df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

print(df.head(10))
