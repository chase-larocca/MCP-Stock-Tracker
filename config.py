import os

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "192.168.1.202")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "trading_db")
DB_USER = os.getenv("DB_USER", "trading_user")
DB_PASS = os.getenv("DB_PASS", "Blank-Salamander-Car2")

# BOT INFORMATION & KEYS
BOT_VERSION = os.getenv("BOT_VERSION", "MCP-BOT:v0.0.1")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# TICKER PROPERTIES
SYMBOL = os.getenv("SYMBOL", "AAPL")

# RISK ASSESSMENT THRESHOLDS
RISK_THRESHOLD = float(os.getenv("RISK_THRESHOLD", 0.5))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.6))
SIGNAL_STRENGTH_THRESHOLD = float(os.getenv("SIGNAL_STRENGTH_THRESHOLD", 0.4))


