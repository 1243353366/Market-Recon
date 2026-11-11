from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from market_recon.data_sources import list_example_watchlist

ROOT = Path(__file__).resolve().parents[1]
WATCHLIST_PATH = ROOT / "data" / "examples" / "sample_watchlist.json"


@st.cache_data
def load_watchlist() -> pd.DataFrame:
    if WATCHLIST_PATH.exists():
        with WATCHLIST_PATH.open("r", encoding="utf-8") as source:
            items = json.load(source)
    else:
        items = list_example_watchlist()
    return pd.DataFrame(items)


st.set_page_config(page_title="Market Recon", page_icon="📈", layout="wide")
st.title("Market Recon")
st.caption("Open-source stock intelligence dashboard")

with st.sidebar:
    st.header("Filters")
    tickers = load_watchlist()["symbol"].tolist()
    selected = st.multiselect("Tracked symbols", tickers, default=tickers[:3])

if not selected:
    st.warning("Choose at least one ticker to view the dashboard.")
    st.stop()

watchlist = load_watchlist()
filtered = watchlist[watchlist["symbol"].isin(selected)].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tracked tickers", len(filtered))
col2.metric("Technology exposure", f"{(filtered['sector'].eq('Technology').sum())}/{len(filtered)}")
col3.metric("Total market cap", f"${filtered['market_cap'].sum():,.0f}")
col4.metric("Status", "Public data")

st.subheader("Watchlist")
st.dataframe(filtered, use_container_width=True)

st.subheader("Research workflow")
with st.container():
    st.markdown(
        """
        - Collect public market data
        - Validate source provenance
        - Compute technical and valuation metrics
        - Generate a structured company report
        - Archive raw and transformed outputs for reproducibility
        """
    )
