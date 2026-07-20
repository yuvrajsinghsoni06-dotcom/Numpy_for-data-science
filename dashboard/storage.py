# ─────────────────────────────────────────────────────────────────────────────
#  storage.py  —  Stage 3: SQLite persistence
#
#  NEW SKILL: instead of keeping data only in memory (a list or DataFrame that
#  disappears when the script exits), we append every snapshot to an SQLite
#  database file.  SQLite ships with Python — no extra install needed.
#
#  Key ideas:
#    • sqlite3.connect() opens (or creates) the .db file
#    • A context manager  (with conn:)  auto-commits on success, rolls back
#      on exception — so you never leave a half-written row
#    • executemany() is faster than looping over execute()
#    • We return pandas DataFrames so Stage 2 (processing.py) works naturally
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3
from datetime import datetime, timezone

import pandas as pd

from config import DB_PATH


# ── Schema ────────────────────────────────────────────────────────────────────

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS price_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fetched_at  TEXT    NOT NULL,   -- ISO-8601 UTC timestamp
    coin        TEXT    NOT NULL,   -- e.g. "bitcoin"
    price_usd   REAL    NOT NULL,
    change_24h  REAL                -- percent change, may be NULL
);
"""

# An index makes repeated  WHERE coin = ?  queries fast
CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_coin_time
    ON price_history (coin, fetched_at);
"""


def init_db() -> None:
    """Create the database file and table if they don't already exist.

    Safe to call multiple times — CREATE IF NOT EXISTS is idempotent.
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.execute(CREATE_INDEX_SQL)
        conn.commit()


# ── Write ─────────────────────────────────────────────────────────────────────

def insert_snapshot(records: list[dict]) -> None:
    """Append a batch of price readings to the database.

    Parameters
    ----------
    records : list of dicts, each with keys:
        coin        – str   e.g. "bitcoin"
        price_usd   – float
        change_24h  – float | None

    Example
    -------
    insert_snapshot([
        {"coin": "bitcoin",  "price_usd": 67234.12, "change_24h": 1.45},
        {"coin": "ethereum", "price_usd": 3512.88,  "change_24h": -0.72},
    ])
    """
    if not records:
        return

    now = datetime.now(timezone.utc).isoformat()

    rows = [
        (now, r["coin"], r["price_usd"], r.get("change_24h"))
        for r in records
    ]

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT INTO price_history (fetched_at, coin, price_usd, change_24h) "
            "VALUES (?, ?, ?, ?)",
            rows,
        )
        conn.commit()


# ── Read ──────────────────────────────────────────────────────────────────────

def load_history(coin: str, limit: int = 500) -> pd.DataFrame:
    """Return the last *limit* rows for *coin* as a DataFrame.

    The DataFrame has columns:
        fetched_at  – datetime (UTC, timezone-aware)
        coin        – str
        price_usd   – float
        change_24h  – float

    Sorted oldest → newest so plotting works naturally.
    """
    sql = """
        SELECT fetched_at, coin, price_usd, change_24h
        FROM price_history
        WHERE coin = ?
        ORDER BY fetched_at DESC
        LIMIT ?
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(sql, conn, params=(coin, limit))

    if df.empty:
        return df

    # Parse the timestamp string into a proper datetime object
    df["fetched_at"] = pd.to_datetime(df["fetched_at"], utc=True)

    # Reverse so rows go oldest → newest
    df = df.iloc[::-1].reset_index(drop=True)
    return df


def row_count(coin: str | None = None) -> int:
    """Return total rows (optionally filtered by coin) — handy for debugging."""
    with sqlite3.connect(DB_PATH) as conn:
        if coin:
            cur = conn.execute(
                "SELECT COUNT(*) FROM price_history WHERE coin = ?", (coin,)
            )
        else:
            cur = conn.execute("SELECT COUNT(*) FROM price_history")
        return cur.fetchone()[0]
