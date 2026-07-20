# ─────────────────────────────────────────────
#  config.py  —  shared constants
# ─────────────────────────────────────────────
import os

# Coins to track (CoinGecko IDs)
COINS = ["bitcoin", "ethereum", "solana"]

# Display names
COIN_LABELS = {
    "bitcoin":  "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "solana":   "Solana (SOL)",
}

# Coin accent colours for charts
COIN_COLORS = {
    "bitcoin":  "#F7931A",
    "ethereum": "#627EEA",
    "solana":   "#9945FF",
}

# How often (seconds) to poll the API and refresh the UI
POLL_INTERVAL = 30

# Rolling-average window (number of data points)
ROLLING_WINDOW = 10

# Anomaly detection — Z-score threshold
Z_THRESHOLD = 2.0

# SQLite database path (sits next to this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "crypto_data.db")

# CoinGecko endpoint
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids={coins}&vs_currencies=usd&include_24hr_change=true"
)
