"""
Live Financial & Indian Stock Market News Aggregator
Fetches real-time market-moving headlines, macro alerts, corporate earnings & RBI/budget updates
for NSE/BSE and Indian indices, with deduplication, priority scoring and date-time stamping.
"""

import time
import urllib.request
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Any

# Curated fallback news in case offline or upstream network throttle
FALLBACK_NEWS = [
    {
        "id": "NEWS_FB_01",
        "title": "RBI Monetary Policy: Focus on Growth & Price Stability as Markets Rally",
        "source": "RBI / Financial Express",
        "is_important": True,
        "type": "NEWS",
        "priority": "HIGH",
        "link": "https://www.rbi.org.in"
    },
    {
        "id": "NEWS_FB_02",
        "title": "FII & DII Inflows: Domestic Institutional Buying Supports Nifty & Bank Nifty",
        "source": "NSE India / Moneycontrol",
        "is_important": True,
        "type": "NEWS",
        "priority": "HIGH",
        "link": "https://www.nseindia.com"
    },
    {
        "id": "NEWS_FB_03",
        "title": "Q2/Q3 Corporate Earnings: Large-Cap Heavyweights Post Strong Profit Margins",
        "source": "LiveMint / Economic Times",
        "is_important": False,
        "type": "NEWS",
        "priority": "NORMAL",
        "link": "https://www.livemint.com"
    }
]

IMPORTANT_KEYWORDS = [
    "RBI", "REPO RATE", "INFLATION", "GDP", "BUDGET", "FED", "RATE CUT",
    "SURGE", "RALLY", "CRASH", "PLUNGE", "RECORD HIGH", "ALL-TIME HIGH",
    "BREAKOUT", "RESULTS", "PROFIT", "LOSS", "SEBI", "WAR", "CRUDE", "VIX",
    "NIFTY", "SENSEX", "BANKNIFTY", "RELIANCE", "HDFC", "TCS", "INFY", "INTELLECT"
]


class MarketNewsFetcher:
    def __init__(self):
        self._cache = {"ts": 0.0, "items": []}
        self._cache_duration = 60.0  # 60s cache

    def fetch_live_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        now = time.time()
        if self._cache["items"] and (now - self._cache["ts"]) < self._cache_duration:
            return self._cache["items"][:limit]

        news_items = []
        try:
            url = "https://news.google.com/rss/search?q=NSE+NIFTY+Indian+stock+market&hl=en-IN&gl=IN&ceid=IN:en"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=4.5) as resp:
                xml_data = resp.read()

            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            for it in items[:limit * 2]:
                title = (it.find("title").text or "").strip()
                if not title:
                    continue

                link = (it.find("link").text or "#").strip()
                pub_date = (it.find("pubDate").text or "").strip()

                # Extract source from title e.g. "Headline - Source Name"
                source = "Market Wire"
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title = parts[0].strip()
                    source = parts[1].strip()

                # Clean HTML tags if any
                title = re.sub(r"<[^>]+>", "", title).strip()

                # Generate clean stable ID based on title content
                clean_key = re.sub(r"[^a-zA-Z0-9]", "", title.lower())[:36]
                item_id = f"NEWS_{clean_key}"

                # Check importance
                title_upper = title.upper()
                is_important = any(kw in title_upper for kw in IMPORTANT_KEYWORDS)

                # JAB TAK KOI CHANGE NA HO TAB TAK SAME NOTIFICATION REPEAT NAHI HONA CHAHIYE:
                if not hasattr(self, "_history"):
                    self._history = {}

                if item_id in self._history:
                    # Headline already fetched previously - reuse existing with original timestamp
                    news_items.append(self._history[item_id])
                else:
                    new_item = {
                        "id": item_id,
                        "title": title,
                        "source": source,
                        "link": link,
                        "type": "NEWS",
                        "priority": "HIGH" if is_important else "NORMAL",
                        "is_important": is_important,
                        "timestamp": time.strftime("%d %b %Y • %I:%M:%S %p"),
                        "pub_date_raw": pub_date
                    }
                    self._history[item_id] = new_item
                    news_items.append(new_item)

                if len(news_items) >= limit:
                    break

        except Exception as e:
            # Fallback to local intelligence items
            pass

        if not news_items:
            # Use fallback with stable timestamp
            if not hasattr(self, "_history"):
                self._history = {}
            for fb in FALLBACK_NEWS:
                fb_id = fb["id"]
                if fb_id not in self._history:
                    self._history[fb_id] = {**fb, "timestamp": time.strftime("%d %b %Y • %I:%M:%S %p")}
                news_items.append(self._history[fb_id])

        self._cache = {"ts": now, "items": news_items}
        return news_items[:limit]


market_news_fetcher = MarketNewsFetcher()
