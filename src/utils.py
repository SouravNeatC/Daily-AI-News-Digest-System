import logging
import sys
from datetime import datetime, timezone

def setup_logging():
    """Configures centralized logging to output to stdout with clean formatting."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    if root.handlers:
        return root
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    return root

logger = logging.getLogger("ai_news_digest")

def get_current_utc_date() -> str:
    """Returns today's date formatted as YYYY-MM-DD in UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def parse_iso_datetime(dt_str: str) -> datetime:
    """Parses standard ISO or RFC datetimes into timezone-aware datetime objects."""
    for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z', '%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z'):
        try:
            dt = datetime.strptime(dt_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return datetime.now(timezone.utc)
