import csv, time, math, sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
BASE="https://books.toscrape.com/"
START=urljoin(BASE, "catalogue/page-1.html")
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
def fetch(url, tries=3, backoff=1.5):
    for i in range(tries):
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
        time.sleep(backoff**(i+1))
    raise RuntimeError(f"Failed to fetch {url} (status {resp.status_code})")
def parse_book(card,page_url):
    title=card.h3.a["title"].strip()
    rel=card.h3.a["href"]
    product_url=urljoin(page_url, rel)
    price=card.select_one(".price_color").get_text(strip=True).replace("£","")
    availability=card.select_one(".availability").get_text(strip=True)
    rating_cls=card.select_one("p.star-rating")["class"]
    rating=next((c for c in rating_cls if c not in ["star-rating"]), "Unknown")
    return {"title":title, "price_gbp":price, "rating":rating, "availability":availability, "url":product_url}
def next_page(soup, current_url):
    nxt=soup.select_one("li.next > a")
    return urljoin(current_url, nxt["href"]) if nxt else None
def scrape_all(start_url=START, out_csv="books.csv"):
    rows, url=[], start_url
    page=1
    while url:
        html=fetch(url)
        soup=BeautifulSoup(html, "html.parser")
        for card in soup.select("article.product_pod"):
            rows.append(parse_book(card, url))
        print(f"Scraped page {page} - total rows: {len(rows)}")
        url=next_page(soup, url)
        page+=1
        time.sleep(0.8)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer=csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return len(rows), out_csv
if __name__=="__main__":
    total, path = scrape_all()
    print(f"\n✅ Done. Saved {total} records to {path}")
