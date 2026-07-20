# ─────────────────────────────────────────────────────────────────────────────
#  ingestion.py  —  Stage 1: hitting a REST API and handling rate limits
#
#  NEW SKILL: the requests library is the standard way Python talks to HTTP
#  APIs.  Key concepts introduced here:
#
#    requests.Session   – reuses the underlying TCP connection (faster for
#                         repeated calls to the same host) and lets you set
#                         default headers once
#    response.raise_for_status()  – turns any 4xx / 5xx into an exception
#                                   so you can't accidentally use bad data
#    Exponential back-off – when you hit a rate-limit (HTTP 429) you wait
#                           longer each retry: 1s, 2s, 4s, 8s, …
#                           This is the standard polite-client pattern.
#
#  Run standalone:  python ingestion.py
#  Imported by:     app.py  (calls fetch_prices() directly)
# ─────────────────────────────────────────────────────────────────────────────

import logging
import time

import requests

from config import COINS, COINGECKO_URL, POLL_INTERVAL
from storage import init_db, insert_snapshot

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Session (reuse TCP connection) ────────────────────────────────────────────
_session = requests.Session()
_session.headers.update({"Accept": "application/json"})


# ── Core fetch function ───────────────────────────────────────────────────────

def fetch_prices(max_retries: int = 5) -> list[dict] | None:
    """Call the CoinGecko API and return a list of price records.

    Returns
    -------
    list of dicts:
        [{"coin": "bitcoin", "price_usd": 67234.12, "change_24h": 1.45}, …]
    None if all retries are exhausted.

    How retries work
    ----------------
    On HTTP 429 (Too Many Requests) or any transient network error we wait
    2**attempt seconds before the next try:

        attempt 0 → wait 1 s
        attempt 1 → wait 2 s
        attempt 2 → wait 4 s
        attempt 3 → wait 8 s
        attempt 4 → wait 16 s  → give up

    This is called "exponential back-off" and is the polite way to handle
    a rate-limited API without hammering it.
    """
    url = COINGECKO_URL.format(coins=",".join(COINS))

    for attempt in range(max_retries):
        try:
            response = _session.get(url, timeout=10)

            # 429 = rate limited — back off and retry
            if response.status_code == 429:
                wait = 2 ** attempt
                log.warning("Rate limited (429). Waiting %ds before retry %d…", wait, attempt + 1)
                time.sleep(wait)
                continue

            # Any other 4xx / 5xx raises an exception immediately
            response.raise_for_status()

            raw: dict = response.json()
            # raw looks like:
            # {
            #   "bitcoin":  {"usd": 67234.12, "usd_24h_change": 1.45},
            #   "ethereum": {"usd": 3512.88,  "usd_24h_change": -0.72},
            # }
            records = []
            for coin, data in raw.items():
                records.append({
                    "coin":       coin,
                    "price_usd":  data.get("usd", 0.0),
                    "change_24h": data.get("usd_24h_change"),
                })

            log.info("Fetched prices for: %s", [r["coin"] for r in records])
            return records

        except requests.exceptions.ConnectionError:
            wait = 2 ** attempt
            log.error("Network error. Retrying in %ds…", wait)
            time.sleep(wait)

        except requests.exceptions.Timeout:
            wait = 2 ** attempt
            log.error("Request timed out. Retrying in %ds…", wait)
            time.sleep(wait)

        except requests.exceptions.RequestException as exc:
            log.error("Unexpected request error: %s", exc)
            return None

    log.error("All %d retries exhausted — skipping this poll.", max_retries)
    return None


# ── Polling loop (standalone use) ─────────────────────────────────────────────

def poll_loop(interval: int = POLL_INTERVAL) -> None:
    """Continuously fetch → store → sleep.

    Runs forever; press Ctrl+C to stop.
    This is useful if you want a *separate* background process feeding the DB
    independently of the Streamlit UI.
    """
    log.info("Starting poll loop — fetching every %ds. Press Ctrl+C to stop.", interval)
    init_db()

    while True:
        records = fetch_prices()
        if records:
            insert_snapshot(records)
            for r in records:
                log.info(
                    "  %-10s  $%,.2f  (24h: %+.2f%%)",
                    r["coin"], r["price_usd"], r.get("change_24h") or 0.0,
                )
        time.sleep(interval)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        poll_loop()
    except KeyboardInterrupt:
        log.info("Poll loop stopped by user.")
