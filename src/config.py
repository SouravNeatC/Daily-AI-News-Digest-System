import os

# Gemini API Configuration
GEMINI_MODEL = "gemini-2.5-flash"

def get_env(name, default=None):
    value = os.environ.get(name)
    if value is None or str(value).strip() == "":
        return default
    return value

def get_int_env(name, default):
    value = get_env(name)
    try:
        return int(value)
    except:
        return default

GEMINI_API_KEY = get_env("GEMINI_API_KEY", "")

# SMTP Configuration
SMTP_SERVER = get_env("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = get_int_env("SMTP_PORT", 587)
SMTP_USER = get_env("SMTP_USER", "")
SMTP_PASSWORD = get_env("SMTP_PASSWORD", "")
TO_EMAIL = get_env("TO_EMAIL", "")
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

# HTML pages that require scraping (Any news portal can be added here dynamically)
HTML_SOURCES = {
    "Anthropic News": {
        "url": "https://www.anthropic.com/news"
    },
    "Google DeepMind": {
        "url": "https://deepmind.google/blog/"
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

# Personal Reader Profile / Custom Persona
# Modify this text to customize how Gemini prioritizes and highlights news for your daily digest
USER_PERSONA = (
    "Interested in new open-source LLM weights, advanced agentic architectures, "
    "local browser-based AI/WebGPU tools, and groundbreaking research papers. "
    "Would like to know about new AI breakthroughs in Medical field."
    "Less interested in high-level corporate partnership announcements, stock prices, or general branding marketing events."
)
