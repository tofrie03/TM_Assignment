import pandas as pd

url = "https://media.githubusercontent.com/media/tofrie03/TM_Assignment/refs/heads/main/Material/Google_trends_Bitcoin.csv"

df_trends = pd.read_csv(url, sep=',')

df_trends.columns = ["Date", "Interest"]
df_trends = df_trends.sort_values("Date")

df_trends.to_csv("renamed_trends.csv", index=False)