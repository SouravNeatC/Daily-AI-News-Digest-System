import re
import string
from utils import logger
from config import AI_KEYWORDS, NEGATIVE_KEYWORDS

TRUSTED_AI_SOURCES = {
    "OpenAI Blog", "Google AI Blog", "Meta Engineering AI", 
    "Microsoft AI Blog", "Hugging Face Blog", "Anthropic News", "Google DeepMind"
}

def normalize_title(title: str) -> str:
    """Normalizes titles to lowercase and strips punctuation/extra whitespace."""
    if not title:
        return ""
    title = title.lower()
    title = title.translate(str.maketrans("", "", string.punctuation))
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def passes_keyword_filter(article: list) -> bool:
    """Returns True if article meets our AI topic relevance criteria."""
    title = article.get("title", "")
    snippet = article.get("snippet", "")
    source = article.get("source", "")
    
    combined_text = f"{title} {snippet}".lower()
    
    for neg_kw in NEGATIVE_KEYWORDS:
        if neg_kw in combined_text:
            logger.info(f"Filtered out (negative keyword '{neg_kw}'): {title}")
            return False
            
    if source in TRUSTED_AI_SOURCES:
        return True
        
    for pos_kw in AI_KEYWORDS:
        if pos_kw in combined_text:
            return True
            
    logger.info(f"Filtered out (no positive keywords): {title}")
    return False

def deduplicate_articles(articles: list) -> list:
    """Removes duplicate articles based on normalized title and link."""
    seen_titles = set()
    seen_links = set()
    unique_articles = []
    
    for art in articles:
        link = art.get("link", "").strip()
        norm_title = normalize_title(art.get("title", ""))
        
        if not norm_title or not link:
            continue
            
        clean_link = link.split("?")[0].rstrip("/")
        
        if norm_title in seen_titles or clean_link in seen_links:
            logger.debug(f"Deduplicated article: {art['title']}")
            continue
            
        seen_titles.add(norm_title)
        seen_links.add(clean_link)
        unique_articles.append(art)
        
    return unique_articles

def filter_articles(articles: list) -> list:
    """Deduplicates and filters articles for AI relevance."""
    deduped = deduplicate_articles(articles)
    filtered = [art for art in deduped if passes_keyword_filter(art)]
    logger.info(f"Articles before filtering: {len(articles)}. After filtering & deduplication: {len(filtered)}")
    return filtered
