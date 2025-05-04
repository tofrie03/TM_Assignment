from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
from selenium.webdriver.common.action_chains import ActionChains
import random
import pandas as pd
import time
import os
from datetime import datetime, timedelta

# Zeitraum für den CSV-Download festlegen
start_fetch = "2022-03-28"
end_fetch = "2025-05-01"

# Pfad zum Download-Verzeichnis
download_dir = os.path.abspath("downloads")

export_dir = os.path.abspath("exports")

# Chrome-Optionen konfigurieren
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": export_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Starte den WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

initials_set = False
first_time = True

def download_csv(start_date, end_date):
    global first_time
    global initials_set
    print(f"📥 Starte Download für Zeitraum: {start_date} bis {end_date}")
    driver.get(f"https://trends.google.es/trends/explore?date={start_date}%20{end_date}&geo=ES&q=%2Fm%2F05p0rrx&hl=de")

    if first_time:
        time.sleep(10)
        first_time = False

    time.sleep(random.uniform(5, 8))  # Realistische Pause

    try:
        # Versuche, ein eventuell sichtbares Cookie-Banner zu entfernen
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cookieBarInner"))
            )
            driver.execute_script("""
                let banner = document.querySelector('.cookieBarInner');
                if (banner) banner.remove();
            """)
            print("🧹 Cookie-Banner entfernt.")
        except:
            print("ℹ️ Kein Cookie-Banner sichtbar oder bereits geschlossen.")

        wait = WebDriverWait(driver, 15)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'fe-line-chart')))
        export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.widget-actions-item.export')))
        export_button.click()
        print("📄 CSV-Download ausgelöst.")
        time.sleep(random.uniform(5, 8))  # Zeit für den Download
    except TimeoutException:
        print("❌ Export-Button nicht gefunden.")

def download_csv_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    current_start = start
    while current_start <= end:
        current_end = min(current_start + timedelta(days=29), end)
        start_str = current_start.strftime("%Y-%m-%d")
        end_str = current_end.strftime("%Y-%m-%d")
        download_csv(start_str, end_str)
        current_start = current_end + timedelta(days=1)

#
# Dummy-Aufruf zur Initialisierung des Sessions-Cookies etc.
# print("🔧 Führe Dummy-Aufruf aus, um Umgebung aufzuwärmen ...")
# driver.get("https://trends.google.es/trends/?geo=ES&hl=de")
# time.sleep(random.uniform(5, 8))  # Realistische Pause

def get_missing_spans():
    df = pd.read_csv(f"{export_dir}/combined_trends.csv")
    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    df = df.dropna(subset=["Datum"]).sort_values("Datum")
    df = df.reset_index(drop=True)

    missing_ranges = {}
    for i in range(1, len(df)):
        previous_date = df.loc[i - 1, "Datum"]
        current_date = df.loc[i, "Datum"]
        diff = (current_date - previous_date).days
        if diff > 1:
            start_date = previous_date + timedelta(days=1)
            end_date = current_date - timedelta(days=1)
            missing_ranges[f"missing_{i}"] = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }

    print("Fehlende Zeiträume:", missing_ranges)
    return missing_ranges


# missing_ranges = get_missing_spans()
# for span in missing_ranges.values():
#     download_csv_range(span["start_date"], span["end_date"])
driver.quit()

# Füge zusätzliche 'multiTimeline'-Dateien zur kombinierten CSV hinzu ...
print("📦 Füge zusätzliche 'multiTimeline'-Dateien zur kombinierten CSV hinzu ...")
additional_files = [f for f in os.listdir(export_dir) if f.startswith("multi") and f.endswith(".csv")]
additional_dfs = []
for file in additional_files:
    try:
        df = pd.read_csv(os.path.join(export_dir, file), skiprows=1)
        df.columns = ["Datum", "Interesse"]
        additional_dfs.append(df)
    except Exception as e:
        print(f"⚠️ Fehler beim Einlesen von {file}: {e}")
if additional_dfs:
    try:
        combined_path = os.path.join(export_dir, "combined_trends.csv")
        combined_df = pd.read_csv(combined_path)
        for df in additional_dfs:
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["Datum"]).sort_values("Datum")
        combined_df.to_csv(combined_path, index=False)
        print("✅ Zusätzliche Dateien erfolgreich hinzugefügt und gespeichert.")
    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren der kombinierten Datei: {e}")
else:
    print("ℹ️ Keine zusätzlichen 'multiTimeline'-Dateien gefunden.")


print("end")