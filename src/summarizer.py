import json
import requests
from config import GEMINI_API_KEY, GEMINI_MODEL
from utils import logger
from dotenv import load_dotenv
load_dotenv()

def summarize_news(clustered_articles: dict) -> dict:
    """Sends all clustered articles to Gemini 2.5 Flash in a single API call to generate a structured JSON digest.
    
    Returns a dict with structured summaries and quick highlights.
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set. Summarization cannot proceed.")
        return {}
        
    payload_data = []
    for cluster_name, articles in clustered_articles.items():
        if not articles:
            continue
        art_list = []
        for art in articles:
            art_list.append({
                "title": art.get("title", ""),
                "link": art.get("link", ""),
                "snippet": art.get("snippet", "")[:300],
                "source": art.get("source", "")
            })
        payload_data.append({
            "cluster": cluster_name,
            "articles": art_list
        })
        
    if not payload_data:
        logger.warning("No articles found to summarize.")
        return {}

    prompt = f"""You are an elite AI technology news editor. Generate a structured Daily AI News Digest from the following clustered articles.

For each cluster, summarize only the major/relevant news items. If there are multiple articles about the exact same announcement, consolidate them.
Keep explanations brief (1-3 lines), highlighting the significance (e.g. model weights available, performance benchmarks, architectural changes). Keep the exact URLs/links associated with the articles.

Also, compile a global "Quick Highlights" list containing 5 to 10 key bullet points of the day's most important takeaways.

Input Articles:
{json.dumps(payload_data, indent=2)}

You must return a JSON response adhering strictly to this schema:
{{
  "clusters": [
    {{
      "name": "Cluster Name",
      "items": [
        {{
          "title": "Article Title",
          "summary": "1 to 3 line explanation.",
          "link": "Article URL Link"
        }}
      ]
    }}
  ],
  "quick_highlights": [
    "Highlight 1...",
    "Highlight 2..."
  ]
}}
"""

    headers = {"Content-Type": "application/json"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }
    
    logger.info(f"Sending single-pass summarization request to {GEMINI_MODEL}...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            logger.error(f"Gemini API returned error: HTTP {response.status_code} - {response.text}")
            return {}
            
        res_json = response.json()
        text_content = res_json["candidates"][0]["content"]["parts"][0]["text"]
        
        result = json.loads(text_content.strip())
        logger.info("Successfully received and parsed structured AI summary.")
        return result
    except Exception as e:
        logger.error(f"Error during Gemini API call or response parsing: {e}")
        return {}
