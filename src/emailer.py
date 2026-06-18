import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, TO_EMAIL
from utils import logger, get_current_utc_date

def generate_html_email(summary_data: dict) -> str:
    """Generates a premium, highly professional news portal styled HTML email from the structured digest data."""
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
            <div class="news-item" style="margin-bottom: 24px; padding-bottom: 20px; border-bottom: 1px dashed #e5e7eb;">
                <div class="news-title" style="margin-bottom: 8px;">
                    <a href="{link}" target="_blank" style="font-family: 'Playfair Display', Georgia, serif; font-size: 18px; font-weight: 700; color: #111827; text-decoration: none; line-height: 1.4;">{title}</a>
                </div>
                <div class="news-summary" style="font-family: 'Inter', Helvetica, Arial, sans-serif; font-size: 14px; color: #4b5563; line-height: 1.6;">{summary}</div>
            </div>
            """
            
        clusters_html += f"""
        <div class="cluster-card" style="background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h2 class="cluster-title" style="font-family: 'Playfair Display', Georgia, serif; font-size: 22px; font-weight: 700; color: #1f2937; margin-top: 0; margin-bottom: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;">{cluster.get('name', 'General AI')}</h2>
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
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
                background-color: #f9fafb;
                color: #1f2937;
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
            
            .masthead {{
                background-color: #fefce8;
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                padding: 24px 20px;
                margin-bottom: 10px;
            }}
            
            .logo-text {{
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 32px;
                font-weight: 700;
                color: #111827;
                margin: 0;
                letter-spacing: 0.5px;
            }}
            
            .date-subtitle {{
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 500;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 2.5px;
                margin-top: 8px;
            }}
            
            .divider {{
                height: 1px;
                background-color: #d1d5db;
                margin: 20px 0;
            }}
            
            .highlights-card {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 24px;
                margin-bottom: 30px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            
            .highlights-title {{
                font-family: 'Playfair Display', Georgia, serif;
                font-size: 20px;
                font-weight: 700;
                color: #1f2937;
                margin-top: 0;
                margin-bottom: 15px;
                border-bottom: 1px solid #e5e7eb;
                padding-bottom: 8px;
            }}
            
            .highlights-card ul {{
                margin: 0;
                padding-left: 20px;
            }}
            
            .highlights-card li {{
                margin-bottom: 12px;
                color: #4b5563;
                font-size: 14.5px;
            }}
            
            footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 12px;
                color: #6b7280;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="masthead">
                    <div class="logo-text">DAILY AI NEWS DIGEST</div>
                    <div class="divider"></div>
                    <div class="date-subtitle">{today}</div>
                </div>
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
    
    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = TO_EMAIL
    
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
