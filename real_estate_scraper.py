"""
High-Profit Investment Scout v2.0
Targets: High-Yield Residential & Commercial Leads
Delivery: Optimized for Gumroad Data Packs & Fiverr Lead Gen
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime

# ── BUSINESS CONFIG ────────────────────────────────────────────────────────
# Switch categories to high-margin niches
TARGETS = {
    "Commercial": "https://www.loopnet.com/search/commercial-real-estate/usa/for-sale/",
    "HighYield_Rentals": "https://sfbay.craigslist.org/search/apa?min_price=5000", # Luxury only
    "Distressed": "https://austin.craigslist.org/search/rfs?query=foreclosure|probate|fixer"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

class ProfitScraper:
    def __init__(self):
        self.master_list = []

    def scrape_commercial(self):
        """Scrapes LoopNet for commercial 'Value-Add' opportunities."""
        print("[$] Scouting Commercial Opportunities...")
        try:
            res = requests.get(TARGETS["Commercial"], headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            # LoopNet structure for 2026
            listings = soup.select('.listing-item, .placard-header') 
            
            for item in listings[:20]: # Quality over quantity
                self.master_list.append({
                    "Type": "Commercial",
                    "Title": item.select_one('.title').text.strip() if item.select_one('.title') else "N/A",
                    "Price": item.select_one('.price').text.strip() if item.select_one('.price') else "Contact Agent",
                    "Location": item.select_one('.location').text.strip() if item.select_one('.location') else "N/A",
                    "Source_URL": item.find('a')['href'] if item.find('a') else "N/A",
                    "Profit_Signal": "Commercial Yield (High Margin)"
                })
        except Exception as e:
            print(f"LoopNet Blocked: {e}")

    def scrape_distressed(self):
        """Finds 'Fixer-Upper' or 'Probate' leads for flippers."""
        print("[$] Scouting Distressed Assets...")
        try:
            res = requests.get(TARGETS["Distressed"], headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('.cl-static-search-result')
            
            for item in items:
                self.master_list.append({
                    "Type": "Fixer/Probate",
                    "Title": item.select_one('.titlestring').text.strip(),
                    "Price": item.select_one('.price').text.strip(),
                    "Location": item.select_one('.location').text.strip() if item.select_one('.location') else "N/A",
                    "Source_URL": item.find('a')['href'],
                    "Profit_Signal": "Investment Opportunity"
                })
        except Exception as e:
            print(f"Distressed Script Error: {e}")

    def save_business_data(self):
        if not self.master_list:
            print("No data found. Check Anti-Bot status.")
            return

        df = pd.DataFrame(self.master_list)
        # Add a timestamped file for Gumroad versions
        stamp = datetime.now().strftime("%Y_%m_%d")
        filename = f"Investment_Leads_{stamp}.csv"
        df.to_csv(filename, index=False)
        print(f"\n[SUCCESS] Profit-Ready Data Saved to {filename}")

if __name__ == "__main__":
    bot = ProfitScraper()
    bot.scrape_commercial()
    bot.scrape_distressed()
    bot.save_business_data()
