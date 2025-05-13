import requests
import os

from config import NEWSAPI_KEY

def get_latest_headline(symbol: str, company_name: str = "Apple") -> str:
    """
    Fetch the latest news headline related to the stock/company.

    :param symbol: Stock ticker (e.g., AAPL)
    :param company_name: Used in keyword search
    :return: Latest news title (string)
    """
    url = (
    "https://newsapi.org/v2/everything?"
    f"q={company_name} OR {symbol}&"
    "sortBy=publishedAt&"
    "language=en&"
    "pageSize=3&"
    "apiKey=" + NEWSAPI_KEY
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data["articles"]:
        return data["articles"][0]["title"] if data["articles"] else f"No recent news found for {company_name}."
    else:
        return f"No recent news found for {company_name}."
