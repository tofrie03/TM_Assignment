import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

url = ""

df = pd.read_csv(url, sep=',')

# Data Cleaning Prozess

# 1. Duplikate entfernen
# Anzahl der Duplikate vor dem Löschen
duplicate_count = df.duplicated().sum()
print("Anzahl der Duplikate vor dem Löschen:", duplicate_count)
df.drop_duplicates(inplace=True)

# 2. Fehlende Werte prüfen und anzeigen
missing_values = df.isnull().sum()
print("Fehlende Werte pro Spalte:\n", missing_values)

# 3. Reihen mit fehlenden Werten entfernen (optional, abhängig vom Bedarf)
df.dropna(inplace=True)

# 4. Datentypen prüfen und gegebenenfalls konvertieren
print("\nDatentypen vor Konvertierung:\n", df.dtypes)

# Konvertiere 'datetime' zu datetime-Objekt
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

# 5. Erneut nach fehlerhaften datetime-Werten prüfen
datetime_na = df['datetime'].isnull().sum()
print("\nUngültige datetime-Werte nach Konvertierung:", datetime_na)

# Entferne Zeilen mit ungültigem datetime
df = df[df['datetime'].notnull()]

# 6. Sortieren nach Datum (optional aber sinnvoll)
df.sort_values(by='datetime', inplace=True)

# 7. Index zurücksetzen
df.reset_index(drop=True, inplace=True)

# 8. Ausgabe der ersten gereinigten Zeilen zur Kontrolle
print("\nErste 5 Zeilen nach Cleaning:\n", df.head())
