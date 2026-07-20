# ─────────────────────────────────────────────────────────────────────────────
#  app.py  —  Stage 4: Streamlit live dashboard
#
#  NEW SKILL: turning a script into an *application*.
#
#  How Streamlit works
#  -------------------
#  Streamlit reruns this entire file top-to-bottom every time:
#    • the user interacts with a widget (sidebar slider, selectbox, …)
#    • st.rerun() is called programmatically (we use this for auto-refresh)
#
#  That means you write plain Python — no callbacks, no event loops, no
#  async — and Streamlit handles all the browser plumbing.
#
#  Key patterns used here
#  ----------------------
#  st.session_state  – a dict that survives reruns; we use it to track when
#                      we last fetched data so we don't hammer the API
#  @st.cache_data    – memoises a function's return value; here it caches the
#                      DB query for a few seconds to avoid re-reading on every
#                      widget interaction
#  st.rerun()        – triggers a fresh top-to-bottom execution of this file,
#                      which is how we implement "auto-refresh every 30 s"
#
#  Run:  streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import time
from datetime import datetime, timezone

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import (
    COIN_COLORS,
    COIN_LABELS,
    COINS,
    POLL_INTERVAL,
    ROLLING_WINDOW,
    Z_THRESHOLD,
)
from ingestion import fetch_prices
from processing import enrich
from storage import init_db, insert_snapshot, load_history, row_count


# ── Page config (must be the very first Streamlit call) ───────────────────────
st.set_page_config(
    page_title="CryptoLens — Live Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global reset */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1923 0%, #0d1520 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * {
    color: #c8d6e5 !important;
}

/* Price cards */
.price-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(12px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.price-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.price-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    border-radius: 16px 16px 0 0;
}
.card-coin    { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #8899aa; margin-bottom: 6px; }
.card-price   { font-size: 1.9rem; font-weight: 700; color: #e8f0fe; letter-spacing: -0.02em; }
.card-change  { font-size: 0.88rem; font-weight: 500; margin-top: 6px; }
.card-rows    { font-size: 0.72rem; color: #556677; margin-top: 4px; }
.up   { color: #00e5a0; }
.down { color: #ff4d6d; }

/* Section headers */
.section-header {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #445566;
    margin: 28px 0 12px;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.25);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: #00e5a0;
    font-weight: 500;
}
.pulse {
    width: 7px; height: 7px;
    background: #00e5a0;
    border-radius: 50%;
    animation: pulse 1.8s infinite;
    display: inline-block;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(0,229,160,0.6); }
    70%  { box-shadow: 0 0 0 7px rgba(0,229,160,0); }
    100% { box-shadow: 0 0 0 0 rgba(0,229,160,0); }
}

/* Anomaly banner */
.anomaly-banner {
    background: linear-gradient(90deg, rgba(255,77,109,0.12), rgba(255,77,109,0.04));
    border: 1px solid rgba(255,77,109,0.3);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.85rem;
    color: #ff8fa3;
    margin-bottom: 12px;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Initialise DB and session state ───────────────────────────────────────────
init_db()

if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = 0.0       # epoch seconds of last API call

if "fetch_count" not in st.session_state:
    st.session_state.fetch_count = 0

if "last_records" not in st.session_state:
    st.session_state.last_records = []      # most recent API response


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")

    selected_coin = st.selectbox(
        "Coin",
        options=COINS,
        format_func=lambda c: COIN_LABELS[c],
        index=0,
    )

    rolling_window = st.slider(
        "Rolling window (points)",
        min_value=2, max_value=50,
        value=ROLLING_WINDOW, step=1,
    )

    z_threshold = st.slider(
        "Anomaly Z-threshold",
        min_value=1.0, max_value=5.0,
        value=float(Z_THRESHOLD), step=0.1,
        help="Points beyond this many std-devs from the rolling mean are flagged",
    )

    show_anomalies = st.toggle("Show anomaly markers", value=True)
    show_rolling   = st.toggle("Show rolling average", value=True)

    st.markdown("---")
    history_limit = st.slider(
        "History to display (points)",
        min_value=20, max_value=500,
        value=200, step=10,
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem; color:#445566;'>"
        f"Polling every <b>{POLL_INTERVAL}s</b><br>"
        "API: CoinGecko (free tier)<br>"
        "Storage: SQLite</div>",
        unsafe_allow_html=True,
    )


# ── Auto-fetch logic ───────────────────────────────────────────────────────────
# We fetch from the API only if POLL_INTERVAL seconds have elapsed since the
# last fetch.  This way widget interactions (slider moves, etc.) don't trigger
# unnecessary API calls.

now = time.time()
seconds_since_fetch = now - st.session_state.last_fetch
should_fetch = seconds_since_fetch >= POLL_INTERVAL

if should_fetch:
    with st.spinner("Fetching live prices…"):
        records = fetch_prices()
    if records:
        insert_snapshot(records)
        st.session_state.last_records = records
        st.session_state.fetch_count += 1
    st.session_state.last_fetch = time.time()


# ── Load & process history ─────────────────────────────────────────────────────
@st.cache_data(ttl=POLL_INTERVAL)
def get_enriched_history(coin: str, limit: int, window: int, z_thresh: float) -> pd.DataFrame:
    """Cache the DB query + pandas transforms for a few seconds.

    ttl=POLL_INTERVAL means the cache expires every 30 s automatically,
    matching our fetch cadence.
    """
    df = load_history(coin, limit=limit)
    if df.empty:
        return df
    return enrich(df, window=window, z_threshold=z_thresh)


df = get_enriched_history(selected_coin, history_limit, rolling_window, z_threshold)

# Most recent values for the live card
latest_records = {r["coin"]: r for r in st.session_state.last_records}
latest = latest_records.get(selected_coin, {})
live_price  = latest.get("price_usd")
live_change = latest.get("change_24h")

# Fall back to DB if session doesn't have this coin yet
if live_price is None and not df.empty:
    live_price  = df["price_usd"].iloc[-1]
    live_change = df["change_24h"].iloc[-1] if "change_24h" in df.columns else None


# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown(
        "<h1 style='font-size:1.8rem; font-weight:700; color:#e8f0fe; margin:0;'>"
        "📈 CryptoLens</h1>"
        "<p style='color:#556677; font-size:0.85rem; margin:2px 0 0;'>"
        "Live prices · Rolling stats · Anomaly detection</p>",
        unsafe_allow_html=True,
    )
with col_status:
    next_fetch_in = max(0, int(POLL_INTERVAL - seconds_since_fetch))
    st.markdown(
        f"<div style='text-align:right; padding-top:8px;'>"
        f"<span class='status-badge'><span class='pulse'></span> LIVE</span><br>"
        f"<span style='font-size:0.7rem; color:#445566;'>next refresh in {next_fetch_in}s</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Live price cards ───────────────────────────────────────────────────────────
st.markdown("<div class='section-header'>Live Prices</div>", unsafe_allow_html=True)

card_cols = st.columns(len(COINS))
snapshot = {r["coin"]: r for r in st.session_state.last_records}

for col, coin in zip(card_cols, COINS):
    data  = snapshot.get(coin, {})
    price = data.get("price_usd")
    chg   = data.get("change_24h")

    if price is None:
        # Try reading latest row from DB
        h = load_history(coin, limit=1)
        if not h.empty:
            price = h["price_usd"].iloc[-1]
            chg   = h["change_24h"].iloc[-1] if "change_24h" in h.columns else None

    price_str = f"${price:,.2f}"  if price is not None else "—"
    chg_str   = f"{chg:+.2f}%"   if chg is not None else "—"
    chg_class = "up" if (chg or 0) >= 0 else "down"
    chg_arrow = "▲" if (chg or 0) >= 0 else "▼"
    accent    = COIN_COLORS.get(coin, "#ffffff")
    n_rows    = row_count(coin)

    with col:
        st.markdown(
            f"<div class='price-card' style='--accent:{accent};'>"
            f"  <div class='card-coin'>{COIN_LABELS.get(coin, coin)}</div>"
            f"  <div class='card-price'>{price_str}</div>"
            f"  <div class='card-change {chg_class}'>{chg_arrow} {chg_str} (24 h)</div>"
            f"  <div class='card-rows'>{n_rows:,} rows stored</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ── Anomaly banner ─────────────────────────────────────────────────────────────
if not df.empty and "anomaly" in df.columns and show_anomalies:
    n_anomalies = int(df["anomaly"].sum())
    if n_anomalies:
        st.markdown(
            f"<div class='anomaly-banner'>⚠️ <b>{n_anomalies} anomalous point{'s' if n_anomalies > 1 else ''}</b> "
            f"detected in the last {len(df)} readings for {COIN_LABELS.get(selected_coin, selected_coin)}</div>",
            unsafe_allow_html=True,
        )


# ── Main chart ────────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='section-header'>"
    f"{COIN_LABELS.get(selected_coin, selected_coin)} — Price History"
    f"</div>",
    unsafe_allow_html=True,
)

accent_color = COIN_COLORS.get(selected_coin, "#7c83fd")

if df.empty:
    st.info("⏳ No data yet — waiting for the first API fetch. This usually takes a few seconds…")
else:
    fig = go.Figure()

    # ── Price line ─────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df["fetched_at"],
        y=df["price_usd"],
        mode="lines",
        name="Price",
        line=dict(color=accent_color, width=2),
        hovertemplate="<b>%{y:$,.2f}</b><br>%{x|%H:%M:%S}<extra></extra>",
    ))

    # ── Rolling average ────────────────────────────────────────────────────
    if show_rolling and "rolling_mean" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["fetched_at"],
            y=df["rolling_mean"],
            mode="lines",
            name=f"Rolling avg ({rolling_window}pt)",
            line=dict(color="rgba(255,255,255,0.4)", width=1.5, dash="dot"),
            hovertemplate="Avg: <b>%{y:$,.2f}</b><extra></extra>",
        ))

    # ── Anomaly markers ────────────────────────────────────────────────────
    if show_anomalies and "anomaly" in df.columns:
        anom = df[df["anomaly"]]
        if not anom.empty:
            fig.add_trace(go.Scatter(
                x=anom["fetched_at"],
                y=anom["price_usd"],
                mode="markers",
                name="Anomaly",
                marker=dict(
                    color="#ff4d6d",
                    size=10,
                    symbol="diamond",
                    line=dict(color="white", width=1),
                ),
                hovertemplate="⚠️ Anomaly<br><b>%{y:$,.2f}</b><br>Z=%{customdata:.2f}<extra></extra>",
                customdata=anom["z_score"],
            ))

    # ── Layout ──────────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#8899aa", size=12),
        margin=dict(l=0, r=0, t=10, b=0),
        height=380,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            showline=False,
            zeroline=False,
            tickprefix="$",
            tickformat=",.0f",
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


# ── Delta chart ────────────────────────────────────────────────────────────────
if not df.empty and "delta_pct" in df.columns:
    delta_df = df.dropna(subset=["delta_pct"])
    if not delta_df.empty:
        st.markdown("<div class='section-header'>Poll-to-Poll % Change</div>", unsafe_allow_html=True)

        colors = [
            "rgba(0,229,160,0.8)" if v >= 0 else "rgba(255,77,109,0.8)"
            for v in delta_df["delta_pct"]
        ]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=delta_df["fetched_at"],
            y=delta_df["delta_pct"],
            marker_color=colors,
            name="Δ%",
            hovertemplate="%{y:+.4f}%<br>%{x|%H:%M:%S}<extra></extra>",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#8899aa", size=12),
            margin=dict(l=0, r=0, t=10, b=0),
            height=180,
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False, zeroline=False),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.04)", showline=False,
                ticksuffix="%", zeroline=True, zerolinecolor="rgba(255,255,255,0.15)",
            ),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)


# ── Recent data table ──────────────────────────────────────────────────────────
if not df.empty:
    st.markdown("<div class='section-header'>Recent Readings</div>", unsafe_allow_html=True)

    display_cols = ["fetched_at", "price_usd", "rolling_mean", "delta_pct", "z_score", "anomaly"]
    available    = [c for c in display_cols if c in df.columns]
    table_df     = df[available].tail(15).iloc[::-1].copy()

    # Format for readability
    if "fetched_at" in table_df.columns:
        table_df["fetched_at"] = table_df["fetched_at"].dt.strftime("%H:%M:%S")
    if "price_usd"    in table_df.columns:
        table_df["price_usd"]    = table_df["price_usd"].map("${:,.2f}".format)
    if "rolling_mean" in table_df.columns:
        table_df["rolling_mean"] = table_df["rolling_mean"].map("${:,.2f}".format)
    if "delta_pct"    in table_df.columns:
        table_df["delta_pct"]    = table_df["delta_pct"].map(lambda v: f"{v:+.4f}%" if pd.notna(v) else "—")
    if "z_score"      in table_df.columns:
        table_df["z_score"]      = table_df["z_score"].map(lambda v: f"{v:.2f}" if pd.notna(v) else "—")

    table_df.columns = [
        c.replace("_", " ").title() for c in table_df.columns
    ]

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
    )


# ── Auto-rerun after POLL_INTERVAL seconds ─────────────────────────────────────
# This is what makes the dashboard "live".  We sleep until it's time to
# fetch again, then call st.rerun() which restarts this script from the top.
#
# Why not just st.rerun() immediately?  Because that would spin at 100% CPU.
# Sleeping the remaining seconds is the polite approach.

time_to_next = max(1, POLL_INTERVAL - int(time.time() - st.session_state.last_fetch))
time.sleep(time_to_next)
st.rerun()
