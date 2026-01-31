import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# Target URL
url = 'https://www.thehimalayantimes.com/'

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.text, features='html.parser')

trending_topics = soup.find_all('h3', class_='alith_post_title')

tr_topics = []

for h3 in trending_topics:
    a_tag = h3.find('a')
    if a_tag:
        tr_topics.append({'title': a_tag.get_text(strip=True), 'link': a_tag['href'], 'scraped_at': datetime.now().isoformat()})

with open('himalayan_times_output.json', 'a', encoding='utf-8') as f:
    json.dump(tr_topics, f, ensure_ascii=False, indent=4)

print(f"Saved records to json file.")

