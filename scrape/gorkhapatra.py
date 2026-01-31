import requests
from bs4 import BeautifulSoup
from datetime import datetime
from googletrans import Translator
import json
import asyncio

# Defining the target URL, Translator() for translation
url = 'https://gorkhapatraonline.com'
translator = Translator()

async def main():
    # Fetch the page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='html.parser')

    article_box = soup.find_all('div', class_='blog-box-layout1')
    articles_data = []

    # articles is in article_box having title and link in 'h2' tag, 
    # (contd.) author in 'ul' tag with class 'entry-meta meta-color-dark' 
    # (contd.) and paragraph in 'div' tag with class 'item-content'.

    for homepage in article_box:
        title_tag = homepage.find('h2', class_='item-title')
        a_tag = title_tag.find('a') if title_tag else None

        title_np = a_tag.get_text(strip=True) if a_tag else None
        link = a_tag['href'] if a_tag else None
        title_en = (await translator.translate(title_np, dest='en')).text if title_np else None

        author_np = None
        ul_class = homepage.select_one('ul.entry-meta.meta-color-dark')
        if ul_class:
            for li in ul_class.find_all('li'):
                if li.find('i', class_='fas fa-user'):
                    author_np = li.get_text(strip=True)
                    break
        author_en = (await translator.translate(author_np, dest='en')).text if author_np else None

        paragraph_np = None
        item_content_div = homepage.find('div', class_='item-content')
        if item_content_div:
            p_tag = item_content_div.find('p')
            if p_tag:
                paragraph_np = p_tag.get_text(strip=True)
        paragraph_en = (await translator.translate(paragraph_np, dest='en')).text if paragraph_np else None

        # Scraping individual article with respective article-link
        # (contd.) available in homepage; with title, author, and paragraph in Nepali, English medium respectively with timestamp.
        articles_data.append({
            'article_link': link,
            'title_nepali': title_np,
            'title_english': title_en,
            'author_nepali': author_np,
            'author_english': author_en,
            'paragraph_nepali': paragraph_np,
            'paragraph_english': paragraph_en,
            'scraped_at': datetime.now().isoformat()
        })

    # Saving the data to a JSON file
    with open('gorkhapatra_output.json', 'a', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)

    print("Articles were saved.")

if __name__ == "__main__":
    asyncio.run(main())
