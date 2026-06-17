import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, TO_EMAIL
from utils import logger, get_current_utc_date

def generate_html_email(summary_data: dict) -> str:
    """Generates a premium, highly aesthetic HTML email from the structured digest data."""
    today = get_current_utc_date()
    
    highlights_html = ""
    for hl in summary_data.get("quick_highlights", []):
        highlights_html += f"<li>{hl}</li>"
        
    clusters_html = ""
    for cluster in summary_data.get("clusters", []):
        items = cluster.get("items", [])
        if not items:
            continue
            
        items_html = ""
        for item in items:
            title = item.get("title", "News Update")
            link = item.get("link", "#")
            summary = item.get("summary", "")
            
            items_html += f"""
            <div class="news-item">
                <div class="news-title">
                    <a href="{link}" target="_blank">{title}</a>
                </div>
                <div class="news-summary">{summary}</div>
            </div>
            """
            
        clusters_html += f"""
        <div class="cluster-card">
            <h2 class="cluster-title">{cluster.get('name', 'General AI')}</h2>
            {items_html}
        </div>
        """
        
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily AI News Digest - {today}</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
            
            body {{
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #0f172a;
                color: #e2e8f0;
                margin: 0;
                padding: 0;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 650px;
                margin: 40px auto;
                padding: 0 20px;
            }}
            
            header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .logo-text {{
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(135deg, #38bdf8 0%, #a855f7 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            }}
            
            .date-subtitle {{
                font-size: 14px;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-top: 5px;
            }}
            
            .highlights-card {{
                background: linear-gradient(145deg, #1e1b4b, #111827);
                border: 1px solid #312e81;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 30px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            }}
            
            .highlights-title {{
                font-size: 18px;
                font-weight: 600;
                color: #818cf8;
                margin-top: 0;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
            }}
            
            .highlights-card ul {{
                margin: 0;
                padding-left: 20px;
            }}
            
            .highlights-card li {{
                margin-bottom: 12px;
                color: #cbd5e1;
            }}
            
            .cluster-card {{
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }}
            
            .cluster-title {{
                font-size: 20px;
                font-weight: 600;
                color: #38bdf8;
                margin-top: 0;
                margin-bottom: 20px;
                border-bottom: 1px solid #334155;
                padding-bottom: 8px;
            }}
            
            .news-item {{
                margin-bottom: 20px;
            }}
            
            .news-item:last-child {{
                margin-bottom: 0;
            }}
            
            .news-title a {{
                color: #f8fafc;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                transition: color 0.2s ease;
            }}
            
            .news-title a:hover {{
                color: #38bdf8;
            }}
            
            .news-summary {{
                color: #94a3b8;
                font-size: 14px;
                margin-top: 6px;
            }}
            
            footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #334155;
                font-size: 12px;
                color: #64748b;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo-text">Daily AI News Digest</div>
                <div class="date-subtitle">{today}</div>
            </header>
            
            <div class="highlights-card">
                <div class="highlights-title">⚡ Quick Highlights</div>
                <ul>
                    {highlights_html}
                </ul>
            </div>
            
            {clusters_html}
            
            <footer>
                <p>Automated Daily Digest System &bull; Powered by Gemini 2.5 Flash</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(summary_data: dict) -> bool:
    """Sends the formatted AI news digest HTML email via SMTP."""
    if not summary_data:
        logger.warning("No summary data to email. Skipping.")
        return False
        
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, TO_EMAIL]):
        logger.error("SMTP credentials or recipient TO_EMAIL are not fully configured. Cannot send email.")
        return False
        
    today = get_current_utc_date()
    subject = f"Daily AI News Digest - {today}"
    html_body = generate_html_email(summary_data)
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    
    msg.attach(MIMEText(html_body, "html"))
    
    try:
        logger.info(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        logger.info("Logging into SMTP server...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        logger.info(f"Sending email to {TO_EMAIL}...")
        server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
        server.quit()
        logger.info("Email sent successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
