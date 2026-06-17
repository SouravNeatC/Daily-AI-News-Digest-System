import os

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

# SMTP Configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "")

# News Feeds Sources (RSS and Fallback Page URLs)
RSS_FEEDS = {
    "OpenAI Blog": "https://openai.com/news/rss.xml",
    "Google AI Blog": "https://blog.google/technology/ai/rss",
    "Meta Engineering Blog": "https://engineering.fb.com/feed/",
    "Microsoft Research Blog": "https://www.microsoft.com/en-us/research/blog/feed/",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "The Decoder": "https://the-decoder.com/feed/"
}

HTML_SOURCES = {
    "Anthropic News": {
        "url": "https://www.anthropic.com/news",
        "type": "anthropic"
    },
    "Google DeepMind": {
        "url": "https://deepmind.google/blog/",
        "type": "deepmind"
    }
}

# Filtering Keywords
AI_KEYWORDS = [
    "ai", "llm", "large language model", "transformer", "neural network", "deep learning", 
    "machine learning", "gpu", "artificial intelligence", "tpu", "diffusion", "rag", 
    "agent", "chatbot", "gpt", "gemini", "claude", "llama", "deepseek", "phi", "mistral",
    "prompt", "fine-tuning", "inference", "training", "huggingface", "pytorch", "tensorflow"
]

# Exclude articles containing these words
NEGATIVE_KEYWORDS = [
    "opinion:", "how to get", "best deals", "gift guide", "sponsored", "podcast episode",
    "newsletter:", "stock price", "stock market", "shares rise", "shares drop", "lawsuit", "sues"
]
