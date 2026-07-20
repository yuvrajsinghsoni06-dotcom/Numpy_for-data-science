# ─────────────────────────────────────────────────────────────────────────────
#  processing.py  —  Stage 2: pandas transformations on the stored history
#
#  This is the part you already know — pure pandas.  The emphasis here is on
#  writing *pure functions* (input → output, no side effects) that can be
#  tested independently and reused anywhere.
#
#  Functions
#  ---------
#  compute_rolling_stats   rolling mean & std (smooths noisy price data)
#  detect_anomalies        Z-score outlier detection
#  compute_deltas          absolute and percentage change since last poll
#  enrich                  convenience: runs all three in sequence
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd

from config import ROLLING_WINDOW, Z_THRESHOLD


# ── Rolling statistics ────────────────────────────────────────────────────────

def compute_rolling_stats(df: pd.DataFrame, window: int = ROLLING_WINDOW) -> pd.DataFrame:
    """Add rolling_mean and rolling_std columns to the price history.

    A rolling mean is the average of the last *window* values — it smooths
    out short-term noise and shows the underlying trend.

    Parameters
    ----------
    df      : DataFrame with at least a 'price_usd' column, sorted oldest→newest
    window  : number of data points in the rolling window (default 10)

    Returns
    -------
    New DataFrame (copy) with two extra columns:
        rolling_mean  – rolling average of price_usd
        rolling_std   – rolling standard deviation of price_usd
    """
    if df.empty:
        return df

    out = df.copy()
    # min_periods=1 means we get a value even for the first few rows
    # (before we have a full window's worth of data)
    out["rolling_mean"] = (
        out["price_usd"]
        .rolling(window=window, min_periods=1)
        .mean()
    )
    out["rolling_std"] = (
        out["price_usd"]
        .rolling(window=window, min_periods=1)
        .std()
        .fillna(0)          # std is NaN for a single row — replace with 0
    )
    return out


# ── Anomaly detection ─────────────────────────────────────────────────────────

def detect_anomalies(df: pd.DataFrame, z_threshold: float = Z_THRESHOLD) -> pd.DataFrame:
    """Flag price spikes / dips using a Z-score test.

    How it works
    ------------
    Z-score = (price - rolling_mean) / rolling_std

    If |Z| > z_threshold (default 2.0), the point is an anomaly — it's more
    than 2 standard deviations away from the recent average.  In a normal
    distribution that happens < 5 % of the time by chance, so anything beyond
    that is suspicious.

    Requires compute_rolling_stats() to have been called first.

    Returns
    -------
    DataFrame with extra columns:
        z_score   – raw Z-score for each row
        anomaly   – boolean True/False flag
    """
    if df.empty or "rolling_mean" not in df.columns:
        return df

    out = df.copy()

    # Avoid division-by-zero when std is 0 (all prices identical)
    std = out["rolling_std"].replace(0, float("nan"))
    out["z_score"] = (out["price_usd"] - out["rolling_mean"]) / std
    out["z_score"] = out["z_score"].fillna(0)

    out["anomaly"] = out["z_score"].abs() > z_threshold
    return out


# ── Delta / change ────────────────────────────────────────────────────────────

def compute_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """Add columns showing how much the price moved since the previous poll.

    Returns
    -------
    DataFrame with extra columns:
        delta_usd  – absolute dollar change  (positive = up, negative = down)
        delta_pct  – percentage change       (positive = up, negative = down)
    """
    if df.empty:
        return df

    out = df.copy()
    out["delta_usd"] = out["price_usd"].diff()          # NaN for the first row
    out["delta_pct"] = out["price_usd"].pct_change() * 100
    return out


# ── Convenience wrapper ───────────────────────────────────────────────────────

def enrich(df: pd.DataFrame, window: int = ROLLING_WINDOW, z_threshold: float = Z_THRESHOLD) -> pd.DataFrame:
    """Run all three transformations in sequence and return the enriched DataFrame.

    This is the function Streamlit calls — one call to get everything.
    """
    df = compute_rolling_stats(df, window=window)
    df = detect_anomalies(df, z_threshold=z_threshold)
    df = compute_deltas(df)
    return df


# ── Quick smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Build a tiny fake DataFrame to verify the functions work
    import numpy as np

    prices = [100, 101, 99, 102, 100, 150, 101, 100, 98, 103]  # 150 is an anomaly
    fake = pd.DataFrame({"price_usd": prices})
    result = enrich(fake)
    print(result[["price_usd", "rolling_mean", "rolling_std", "z_score", "anomaly", "delta_usd"]].to_string())
    print(f"\nAnomalies detected: {result['anomaly'].sum()}")
