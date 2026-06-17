import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Inject src folder into python path for importing modules cleanly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from utils import setup_logging, logger
from news_fetcher import fetch_all_news
from filter import filter_articles
from cluster import cluster_articles
from summarizer import summarize_news
from emailer import send_email, generate_html_email

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Daily AI News Digest Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Fetch, filter, cluster, and summarize, but do not send the email.")
    args = parser.parse_args()
    
    logger.info("Starting Daily AI News Digest System...")
    
    logger.info("Fetching articles...")
    raw_articles = fetch_all_news()
    if not raw_articles:
        logger.info("No new articles found. Exiting.")
        return
        
    logger.info("Filtering and deduplicating articles...")
    filtered_articles = filter_articles(raw_articles)
    if not filtered_articles:
        logger.info("No articles remained after filtering. Exiting.")
        return
        
    logger.info("Clustering articles...")
    clustered = cluster_articles(filtered_articles)
    
    logger.info("Generating AI Summaries...")
    summary_data = summarize_news(clustered)
    if not summary_data:
        logger.error("Failed to generate AI summaries. Exiting.")
        return
        
    if args.dry_run:
        logger.info("Dry-run flag detected. Generating HTML digest preview file instead of emailing.")
        html_email = generate_html_email(summary_data)
        preview_file = "digest_preview.html"
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html_email)
        logger.info(f"Dry-run complete. HTML preview written to: {os.path.abspath(preview_file)}")
        
        print("\n--- QUICK HIGHLIGHTS PREVIEW ---")
        for hl in summary_data.get("quick_highlights", []):
            print(f"- {hl}")
        print("--------------------------------\n")
    else:
        logger.info("Sending news digest email...")
        success = send_email(summary_data)
        if success:
            logger.info("Daily news digest successfully completed!")
        else:
            logger.error("Failed to complete email delivery.")

if __name__ == "__main__":
    main()
