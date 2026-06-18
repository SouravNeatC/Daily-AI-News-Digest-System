import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import urllib.parse
import re

from config import RSS_FEEDS, HTML_SOURCES
from utils import logger, parse_iso_datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_rss_xml(xml_text: str) -> list:
    """Parses RSS or Atom XML content and returns a list of raw article dicts."""
    articles = []
    if not xml_text:
        return articles

    try:
        xml_text = xml_text.strip()
        root = ET.fromstring(xml_text)
    except Exception as e:
        logger.error(f"Failed to parse XML string: {e}")
        return articles

    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_date_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            snippet = desc_el.text if desc_el is not None else ""
            pub_date_str = pub_date_el.text if pub_date_el is not None else ""

            articles.append({
                "title": title.strip() if title else "",
                "link": link.strip() if link else "",
                "snippet": snippet.strip() if snippet else "",
                "pub_date_str": pub_date_str.strip()
            })
        return articles

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//atom:entry", ns)
    if not entries:
        entries = root.findall(".//entry")

    for entry in entries:
        title_el = entry.find("atom:title", ns) or entry.find("title")
        title = title_el.text if title_el is not None else ""

        link_el = entry.find("atom:link", ns) or entry.find("link")
        link = ""
        if link_el is not None:
            link = link_el.attrib.get("href", link_el.text or "")

        if not link and link_el is not None:
            link = link_el.attrib.get("href", "")

        snippet_el = entry.find("atom:summary", ns) or entry.find("summary") or entry.find("atom:content", ns) or entry.find("content")
        snippet = snippet_el.text if snippet_el is not None else ""

        pub_date_el = entry.find("atom:published", ns) or entry.find("published") or entry.find("atom:updated", ns) or entry.find("updated")
        pub_date_str = pub_date_el.text if pub_date_el is not None else ""

        articles.append({
            "title": title.strip() if title else "",
            "link": link.strip() if link else "",
            "snippet": snippet.strip() if snippet else "",
            "pub_date_str": pub_date_str.strip()
        })

    return articles

def fetch_rss_sources() -> list:
    """Fetches all configured RSS feeds and returns a list of raw articles."""
    all_articles = []
    
    for name, url in RSS_FEEDS.items():
        logger.info(f"Fetching RSS feed from {name}: {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                articles = parse_rss_xml(response.text)
                logger.info(f"Successfully fetched {len(articles)} articles from {name}")
                for art in articles:
                    art["source"] = name
                all_articles.extend(articles)
            else:
                logger.warning(f"Failed to fetch {name}: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching RSS source {name}: {e}")
            
    return all_articles

def fetch_generic_html(name: str, config: dict) -> list:
    """Scrapes news articles from any HTML news/blog page dynamically by extracting links, titles, and nearby dates."""
    url = config.get("url")
    if not url:
        return []
        
    logger.info(f"Scraping dynamic HTML source '{name}': {url}")
    articles = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch HTML source {name}: HTTP {response.status_code}")
            return articles
            
        soup = BeautifulSoup(response.text, "html.parser")
        parsed_url = urllib.parse.urlparse(url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Look for links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
                
            # Filter obvious noise
            lower_href = href.lower()
            exclude_keywords = [
                "/tag/", "/category/", "/author/", "/legal/", "/privacy/", "/terms/", 
                "/about", "/contact", "/careers", "/search", "/login", "/signup", "/subscribe",
                "twitter.com", "facebook.com", "linkedin.com", "github.com", "instagram.com"
            ]
            if any(kw in lower_href for kw in exclude_keywords):
                continue
                
            # Resolve to absolute URL
            full_url = urllib.parse.urljoin(url, href)
            
            # Restrict to the same domain/subdomain
            parsed_full = urllib.parse.urlparse(full_url)
            if parsed_full.netloc != parsed_url.netloc and not parsed_full.netloc.endswith("." + parsed_url.netloc.split(".")[-2] + "." + parsed_url.netloc.split(".")[-1]):
                continue
                
            # Get the title text
            title_text = ""
            header_el = a_tag.find(["h1", "h2", "h3", "h4", "h5", "h6", "div", "span"])
            if header_el:
                title_text = header_el.get_text()
            else:
                title_text = a_tag.get_text()
                
            title_text = re.sub(r'\s+', ' ', title_text).strip()
            # Title should be a reasonable length for a news headline
            if not title_text or len(title_text) < 12 or len(title_text) > 200:
                continue
                
            # Skip common generic button texts
            lower_title = title_text.lower()
            boilerplate = ["read more", "learn more", "subscribe", "newsletter", "terms", "privacy", "about us", "contact", "careers", "search", "menu", "sign in", "sign up", "all posts", "back to top"]
            if any(bp in lower_title for bp in boilerplate):
                continue
                
            # Scan nearby text in parent/ancestors for dates
            date_str = ""
            parent = a_tag.parent
            for _ in range(4):
                if parent is None:
                    break
                text = parent.get_text()
                # 1. "June 18, 2026" or "Jun 18, 2026"
                m1 = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', text, re.IGNORECASE)
                if m1:
                    date_str = m1.group(0)
                    break
                # 2. "18 June 2026" or "18 Jun 2026"
                m2 = re.search(r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b', text, re.IGNORECASE)
                if m2:
                    date_str = m2.group(0)
                    break
                # 3. ISO format "YYYY-MM-DD"
                m3 = re.search(r'\b\d{4}[-/]\d{2}[-/]\d{2}\b', text)
                if m3:
                    date_str = m3.group(0)
                    break
                parent = parent.parent
                
            articles.append({
                "title": title_text,
                "link": full_url,
                "snippet": "",
                "pub_date_str": date_str,
                "source": name
            })
    except Exception as e:
        logger.error(f"Error scraping HTML source '{name}': {e}")
        
    # Deduplicate articles based on link
    unique_articles = []
    seen = set()
    for art in articles:
        if art["link"] not in seen:
            seen.add(art["link"])
            unique_articles.append(art)
            
    logger.info(f"Scraped {len(unique_articles)} articles from '{name}'")
    return unique_articles

def filter_last_24_hours(articles: list) -> list:
    """Filters articles to include only those published in the last 24 hours."""
    filtered = []
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(hours=24)
    
    for art in articles:
        pub_str = art.get("pub_date_str", "")
        if not pub_str:
            art["pub_date"] = now
            filtered.append(art)
            continue
            
        dt = parse_iso_datetime(pub_str)
        art["pub_date"] = dt
        if dt >= threshold:
            filtered.append(art)
        else:
            logger.debug(f"Filtering out old article: '{art['title']}' ({pub_str})")
            
    return filtered

def fetch_all_news() -> list:
    """Main function to gather all raw news articles from all sources and filter to last 24h."""
    articles = []
    articles.extend(fetch_rss_sources())
    
    # Dynamically iterate over all HTML sources defined in config.py
    for name, config in HTML_SOURCES.items():
        articles.extend(fetch_generic_html(name, config))
        
    recent_articles = filter_last_24_hours(articles)
    logger.info(f"Total raw articles fetched: {len(articles)}. After 24h filter: {len(recent_articles)}")
    return recent_articles
