# import nltk
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download()


import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def get_bitcoin_price():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return float(soup.find("span", class_="sc-65e7f566-0 esyGGG base-text").text[1:].replace(',', ''))

def get_bitcoin_lowest():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return float(soup.find("div", class_="sc-65e7f566-0 eQBACe flexBetween").find("span").text[1:].replace(',', ''))

def get_bitcoin_news():
    url = "https://bitcoinnews.com/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    news = soup.find_all("h5")
    return [n.text for n in news]

def get_bitcoin_sentiment(debug=False):
    sia = SentimentIntensityAnalyzer()
    sentiment = 0
    n_sentiment = 0
    news = get_bitcoin_news()
    for n in news:
        s = sia.polarity_scores(n)['compound']
        if s != 0:
            sentiment += s
            n_sentiment += 1
            if debug:
                print(f'"{n}" -> {sia.polarity_scores(n)}')
    return sentiment / n_sentiment

def should_i_buy():
    low = get_bitcoin_lowest()
    price = get_bitcoin_price()
    sentiment = get_bitcoin_sentiment()

    if price < low and sentiment > 0.5:
        return "Yes, let's do it"
    if price > low and sentiment > 0.5:
        return "SHUT UP AND TAKE MY MONEY"
    if price < low and sentiment < 0.2:
        return "Better run"
    else:
        return "Not a good time"

price = get_bitcoin_price()

lowest = get_bitcoin_lowest()

news = get_bitcoin_news()

sentiment = get_bitcoin_sentiment()

buy = should_i_buy()

print(news)

with open("output.txt", "w") as file:
    file.write(news)

print("End of the program")

