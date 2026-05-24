import warnings
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib3.exceptions import InsecureRequestWarning

# Silence SSL warnings (some IR news sites have broken SSL)
warnings.simplefilter("ignore", InsecureRequestWarning)

PERSIAN_SOURCES = {
    "mehr": "https://www.mehrnews.com/rss",
    "yjc": "https://www.yjc.ir/fa/rss/allnews",
    "eghtesadonline": "https://www.eghtesadonline.com/fa/rss/allnews",
    "zoomit": "https://www.zoomit.ir/feed/",
    "digiato": "https://digiato.com/feed",
}

ENGLISH_SOURCES = {
    "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
    "reuters": "https://www.reutersagency.com/feed/?best-topics=technology",
    "nyt": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "verge": "https://www.theverge.com/rss/index.xml",
}

NEWS_SOURCES = {**PERSIAN_SOURCES, **ENGLISH_SOURCES}


def fetch_rss(rss_url: str, source_name: str):
    """
    Fetch a single RSS feed and return a list of articles.

    Each article is a dict:
    {
        "source": str,       # e.g. "zoomit"
        "title": str,
        "link": str,
        "description": str,
        "pub_date": datetime | None,
    }
    """
    try:
        # NOTE: verify=False because some news sites have invalid SSL configs.
        response = requests.get(rss_url, timeout=10, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Network error while fetching '{source_name}': {e}")
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"[ERROR] XML parse error for '{source_name}': {e}")
        return []

    # Some feeds use <rss><channel><item>, some have slightly different nesting.
    # .//item makes this more robust across different structures.
    items = root.findall(".//item")
    if not items:
        print(f"[WARN] No <item> elements found for '{source_name}'.")
        return []

    articles = []

    for item in items:
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        description = item.findtext("description", default="").strip()

        # Parse pubDate if present
        pub_date_str = item.findtext("pubDate", default="").strip()
        pub_date = None
        if pub_date_str:
            try:
                pub_date = parsedate_to_datetime(pub_date_str)
            except (TypeError, ValueError):
                pub_date = None

        articles.append(
            {
                "source": source_name,
                "title": title,
                "link": link,
                "description": description,
                "pub_date": pub_date,
            }
        )

    return articles


def fetch_multiple_sources(source_keys):
    """
    Fetch RSS feeds for the given list of source keys and return a merged list.

    source_keys example: ["mehr", "zoomit"]
    """
    all_articles = []

    for key in source_keys:
        if key not in NEWS_SOURCES:
            print(f"[WARN] Unknown source key: '{key}' (skipped).")
            continue

        url = NEWS_SOURCES[key]
        articles = fetch_rss(url, source_name=key)
        all_articles.extend(articles)

    # Sort by pub_date (newest first). Articles without pub_date go to the end.
    all_articles.sort(
        key=lambda x: x["pub_date"] or datetime.min.replace(tzinfo=None),
        reverse=True,
    )

    return all_articles


if __name__ == "__main__":
    # Simple CLI for manual testing
    user_input = input(
        "Enter sources (comma-separated, e.g. mehr,zoomit,digiato): "
    ).strip()

    if not user_input:
        print("No sources provided. Exiting.")
    else:
        chosen_sources = [s.strip() for s in user_input.split(",")]
        articles = fetch_multiple_sources(chosen_sources)

        print(f"\nFetched {len(articles)} articles.\n")

        # Show first 10 articles as a sample
        for article in articles[:10]:
            pub = (
                article["pub_date"].strftime("%Y-%m-%d %H:%M")
                if article["pub_date"]
                else "No Date"
            )
            print(f"[{article['source'].upper()}] ({pub}) {article['title']}")
            print(f"Link: {article['link']}")
            if article["description"]:
                print(f"Description: {article['description'][:150]}...")
            print("-" * 80)
