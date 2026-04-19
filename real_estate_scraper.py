"""
Real Estate Listing Scraper
============================
Scrapes rental/sale listings from Craigslist housing section.
Craigslist is legal to scrape (no login required, public data).

Output: real_estate_data.csv  (ready to sell or analyze)

Usage:
    pip install requests beautifulsoup4
    python real_estate_scraper.py

Customize:
    - Change CITY to any Craigslist city code (sfbay, chicago, austin, etc.)
    - Change CATEGORY: 'apa' = apartments, 'rfs' = houses for sale
    - Change MAX_PAGES to scrape more listings
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────
CITY = "sfbay"          # Craigslist city code
CATEGORY = "apa"        # apa=apartments for rent, rfs=real estate for sale
MAX_PAGES = 3           # Each page has ~120 listings (3 pages = ~360 listings)
OUTPUT_FILE = "real_estate_data.csv"

BASE_URL = f"https://{CITY}.craigslist.org/search/{CATEGORY}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
# ────────────────────────────────────────────────────────────────────────────


def get_listings_page(start: int) -> list[dict]:
    """Fetch one page of listings and return list of listing dicts."""
    params = {"start": start}
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  [!] Request failed (start={start}): {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Craigslist wraps each listing in <li class="cl-search-result">
    for item in soup.select("li.cl-search-result"):
        try:
            title_el = item.select_one("a.cl-app-anchor span[id]")
            title = title_el.get_text(strip=True) if title_el else "N/A"

            link_el = item.select_one("a.cl-app-anchor")
            link = link_el["href"] if link_el else "N/A"

            price_el = item.select_one(".priceinfo")
            price = price_el.get_text(strip=True) if price_el else "N/A"

            meta_el = item.select_one(".cl-csite-post-meta")
            meta = meta_el.get_text(" ", strip=True) if meta_el else "N/A"

            # Beds/baths often in housing-specific meta
            beds_el = item.select_one(".housing")
            beds = beds_el.get_text(strip=True) if beds_el else "N/A"

            location_el = item.select_one(".supertitle")
            location = location_el.get_text(strip=True) if location_el else "N/A"

            date_el = item.select_one("div.meta span.date")
            date = date_el.get_text(strip=True) if date_el else "N/A"

            results.append({
                "title": title,
                "price": price,
                "beds_baths": beds,
                "location": location,
                "date_posted": date,
                "url": link,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "city": CITY,
                "category": CATEGORY,
            })
        except Exception as e:
            print(f"  [!] Skipped one listing: {e}")
            continue

    return results


def scrape_all() -> list[dict]:
    """Scrape MAX_PAGES pages and return all listings."""
    all_listings = []
    for page in range(MAX_PAGES):
        start = page * 120
        print(f"  Scraping page {page + 1}/{MAX_PAGES} (offset {start})...")
        listings = get_listings_page(start)
        all_listings.extend(listings)
        print(f"    Found {len(listings)} listings (total so far: {len(all_listings)})")
        # Polite delay — avoid hammering the server
        if page < MAX_PAGES - 1:
            delay = random.uniform(1.5, 3.0)
            time.sleep(delay)
    return all_listings


def save_to_csv(listings: list[dict], filename: str):
    """Save listings to a CSV file."""
    if not listings:
        print("No listings to save.")
        return
    fields = list(listings[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(listings)
    print(f"\n  Saved {len(listings)} listings to '{filename}'")


def print_summary(listings: list[dict]):
    """Print a quick summary of what was scraped."""
    priced = [l for l in listings if l["price"] not in ("N/A", "")]
    print(f"\n{'='*50}")
    print(f"  SCRAPE SUMMARY")
    print(f"{'='*50}")
    print(f"  Total listings : {len(listings)}")
    print(f"  With price     : {len(priced)}")
    print(f"  City           : {CITY}")
    print(f"  Category       : {CATEGORY}")
    if listings:
        print(f"\n  Sample listing:")
        s = listings[0]
        print(f"    Title    : {s['title']}")
        print(f"    Price    : {s['price']}")
        print(f"    Location : {s['location']}")
        print(f"    URL      : {s['url']}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    print(f"\nReal Estate Scraper starting...")
    print(f"  Target : {CITY}.craigslist.org/{CATEGORY}")
    print(f"  Pages  : {MAX_PAGES}\n")

    listings = scrape_all()
    print_summary(listings)
    save_to_csv(listings, OUTPUT_FILE)

    print("Done! Open real_estate_data.csv to see your data.")
