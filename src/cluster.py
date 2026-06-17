from utils import logger

CLUSTERS = {
    "New LLM Releases": [
        "release", "launch", "weights", "llama", "claude", "mistral", 
        "gpt-4", "gpt-5", "gemma", "phi-", "deepseek", "qwen", "stable diffusion", 
        "whisper", "sora", "generative model", "checkpoint", "llm"
    ],
    "Research Breakthroughs": [
        "research", "paper", "breakthrough", "architecture", "benchmark", "dataset", 
        "evaluation", "arxiv", "training", "reinforcement learning", "rlhf", "dpo", 
        "reasoning", "agentic", "cognitive", "proof", "science", "medical"
    ],
    "Open Source AI Tools": [
        "open source", "open-source", "github", "repo", "library", "framework", 
        "tooling", "langchain", "llamaindex", "pytorch", "huggingface", "transformers", 
        "vllm", "ollama", "sdk", "api", "developer"
    ],
    "Big Tech Updates": [
        "openai", "google", "meta", "microsoft", "anthropic", "apple", "nvidia", 
        "amazon", "cohere", "midjourney"
    ],
    "AI Industry News": [
        "startup", "funding", "invests", "acquisition", "partnership", "regulation", 
        "policy", "eu ai act", "chips", "gpu", "factory", "market", "demand", "ceo"
    ]
}

def cluster_articles(articles: list) -> dict:
    """Groups articles into predefined clusters using deterministic keyword matching."""
    clustered = {name: [] for name in CLUSTERS.keys()}
    
    for art in articles:
        title = art.get("title", "").lower()
        snippet = art.get("snippet", "").lower()
        source = art.get("source", "").lower()
        combined_text = f"{title} {snippet} {source}"
        
        matched_cluster = None
        
        for cluster_name, keywords in CLUSTERS.items():
            if any(kw in combined_text for kw in keywords):
                matched_cluster = cluster_name
                break
                
        if not matched_cluster:
            matched_cluster = "AI Industry News"
            
        clustered[matched_cluster].append(art)
        
    for name, arts in clustered.items():
        logger.info(f"Cluster '{name}': {len(arts)} articles")
        
    return clustered
