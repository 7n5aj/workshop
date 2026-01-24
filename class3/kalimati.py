import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import csv
import time

BASE_URL = "https://kalimatimarket.gov.np/price"

# request post
def fetch_price_by_date(target_date):
    payload = {
        "from": target_date,
        "to": target_date
    }

    r = requests.post(BASE_URL, data=payload, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

# parse beautiful soup
def extract_table(soup):
    table = soup.select_one("div.pro-info table")
    if not table:
        return []

    rows = table.find_all("tr")
    data = []

# response html 
    for row in rows[1:]: 
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if cols:
            data.append(cols)
    return data

# testing for single date
soup = fetch_price_by_date("2025-01-20")
rows = extract_table(soup)

for r in rows[:5]:
    print(r)

# data extraction
def export_to_csv(rows, filename):
    headers = ["commodity", "unit", "min", "max", "avg"]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for row in rows:
            if len(row) >= 5:
                writer.writerow(row[:5])

export_to_csv(rows, "kalimati.csv")


# does this code helps to extract the vegetable details where the form works upon the POST 
# (contd.) and input is taken as token value from the form
# (contd.) and the table is in the div 'pro-info' with table id "commodityPriceParticular"
# (contd.) need the data in csv format as well
# (contd.) also i need the data in english language how can we work in this particular case
# (contd.) for your reference i have attached the html file within this repository
