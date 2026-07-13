import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
DB_URL          = os.getenv("DATABASE_URL", "postgresql://root:password@localhost/price_monitor_db")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL_HOURS", 24))
PROXY_LIST      = os.getenv("PROXY_LIST", "").split(",")
USER_AGENTS     = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0 Safari/537.36",
]
PRICE_DROP_ALERT_THRESHOLD   = float(os.getenv("PRICE_DROP_THRESHOLD",   5.0))   # percent
PRICE_SPIKE_ALERT_THRESHOLD  = float(os.getenv("PRICE_SPIKE_THRESHOLD",  10.0))  # percent
