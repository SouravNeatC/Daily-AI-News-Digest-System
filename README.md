# Daily AI News Digest System ⚡📰

A production-quality, lightweight, and highly optimized automated system to fetch, filter, cluster, summarize, and deliver daily AI news updates straight to your inbox. 

It is designed specifically for **maximum runtime efficiency, zero browser automation overhead, and minimal API costs** in GitHub Actions.

---

## 🏗️ Project Structure

```text
/ai-news-reporter
  ├── .github/workflows/
  │     └── daily.yml          # GitHub Actions workflow (runs daily at 8:00 AM UTC)
  ├── src/
  │     ├── config.py          # News sources, Gemini model config, negative filters, and user persona
  │     ├── utils.py           # Structured logger and date utilities
  │     ├── news_fetcher.py    # RSS parsing & dynamic generic HTML scrapers
  │     ├── filter.py          # Title normalization, deduplication, and keyword filtration
  │     ├── cluster.py         # Embedding-free deterministic topic clustering
  │     ├── summarizer.py      # Resilient, persona-tailored single-pass Gemini client
  │     └── emailer.py         # SMTP email formatter (premium newspaper HTML design)
  ├── main.py                  # Entrypoint orchestrator
  ├── requirements.txt         # Minimal dependency definitions
  └── README.md                # System documentation
```

---

## ⚡ Key Optimizations & Features

- **Personalized Reader Profile:** Tailor the daily news coverage using `USER_PERSONA` in `src/config.py` to instruct Gemini to prioritize, filter, and summarize articles matching your specific tech interests.
- **Dynamic HTML news scraping:** Iterates dynamically over any arbitrary news portal added to `HTML_SOURCES` in `config.py` using a single generic HTML news scraper.
- **API Resilience (Auto-Retry):** Automatically retries Gemini API requests up to 4 times with exponential backoff if a transient error (such as HTTP `503` or rate limit `429`) is encountered.
- **Single-Pass Summarization:** Packages all clustered articles into a single prompt for Gemini 2.5 Flash, reducing the LLM execution footprint to **exactly 1 call per run**.
- **No Browser Automation:** Uses lightweight `requests` and XML/HTML parsing (BeautifulSoup) to extract feeds, bringing ingestion times down to milliseconds.
- **Embedding-Free Clustering:** Clusters topics deterministically using rule-based term-matching to bypass costly vector database integrations and embedding calls.
- **Fast Startup:** Only requires two lightweight dependencies (`requests`, `beautifulsoup4`), yielding extremely fast workflow initialization in GitHub Actions.

---

## ⚙️ Setup & Configuration

### 1. Local Setup

Ensure you have Python 3.9+ installed. Install the dependencies:

```bash
pip install -r requirements.txt
```

Set up your environment variables locally:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-smtp-app-password"
export TO_EMAIL="recipient-email@gmail.com"
```

Configure your RSS feeds, dynamic HTML portals, and personalized interests in `src/config.py` using `RSS_FEEDS`, `HTML_SOURCES`, and `USER_PERSONA`.

### 2. GitHub Secrets

To automate the daily runs, push the repository to GitHub and add the following **Repository Secrets** under `Settings > Secrets and variables > Actions`:

| Secret Name | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Key |
| `SMTP_SERVER` | SMTP Server Host (e.g., `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP Server Port (e.g., `587`) |
| `SMTP_USER` | Sending Email Address |
| `SMTP_PASSWORD` | App-specific password for SMTP authentication |
| `TO_EMAIL` | Destination Email Address for digest delivery |

---

## 🚀 Usage

### Run Dry Run (With Live Fetching & Gemini)
To fetch actual news and call the Gemini API without dispatching an email:
```bash
python3 main.py --dry-run
```
This writes the generated HTML digest newsletter preview to `./digest_preview.html` and prints highlights to the log console.

### Full Execution (With Email Delivery)
```bash
python3 main.py
```
