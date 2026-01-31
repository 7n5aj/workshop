import requests
from bs4 import BeautifulSoup
import json

url = "https://myrepublica.nagariknetwork.com"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# trending articles are defined in div with class "lg:mb-0 mb-8"
trending_articles = soup.find_all("div", class_="lg:mb-0 mb-8")

# extracting the links of the trending articles
trending_path = []
for each_topic in trending_articles:
    a_tag = each_topic.find("a", href=True)
    if a_tag:
        trending_path.append(a_tag["href"])

trending_articles_links = []
for each_path in trending_path:
    full_url = each_path
    trending_articles_links.append(full_url)

# extracting title, category, content from each article
articles_data = []

for topic, article_url in zip(trending_articles, trending_articles_links):

    # title
    title_tag = topic.find("h1", class_="rep-headline--medium")
    title = title_tag.get_text(strip=True) if title_tag else None

    # category
    category_tag = topic.find("span", class_="rep-misc__tag")
    category = category_tag.get_text(strip=True) if category_tag else None

    # content
    content_tag = topic.find("p", class_="text-neutral-dark-gray")
    content = content_tag.get_text(strip=True) if content_tag else None

    articles_data.append({
        "title": title,
        "category": category,
        "content": content,
        "article_link": article_url
    })

# saving the data to a JSONL file
with open("myrepublica_output.jsonl", "a", encoding="utf-8") as f:
    for article in articles_data:
        f.write(json.dumps(article, ensure_ascii=False) + "\n")

print("Saved records to jsonl file.")
