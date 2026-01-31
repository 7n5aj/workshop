import requests
from bs4 import BeautifulSoup
import asyncio
from googletrans import Translator
import csv

BASE_URL = "https://kalimatimarket.gov.np/price"

def fetch_price_by_date(target_date):
    payload = {
        "datePricing": target_date
    }

    with requests.Session() as session:
        # Use session cause website uses cookies to prevent against csrf attack
        r = session.get(BASE_URL, data=payload, timeout=10)
        page = BeautifulSoup(r.text, "html.parser")
        token = page.find("input", {"name": "_token"})["value"]
        payload["_token"] = token
        r = session.post(BASE_URL, data=payload, timeout=10)
        with open("kalimati.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

async def extract_table(soup):
    table = soup.find("table", id="commodityPriceParticular")
    if not table:
        return []
    rows = table.find_all("tr")
    data = []
    translator = Translator()
    for row in rows[1:]:
        texts = [td.get_text(strip=True) for td in row.find_all("td")]
        # Create coroutines for all translations
        coros = [translator.translate(text, dest='en') for text in texts]
        translations = await asyncio.gather(*coros)
        translated_texts = [tr.text for tr in translations]
        # You can now use translated_texts as needed
        data.append(translated_texts)
        
    return data


async def main():
    target_date = "2026-01-31"  # Example date
    soup = fetch_price_by_date(target_date)
    table_data = await extract_table(soup)
    with open('kalimati_output.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(table_data)
    
if __name__ == "__main__":
    asyncio.run(main())