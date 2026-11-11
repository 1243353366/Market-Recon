from __future__ import annotations

import streamlit as st

from market_recon.investor_library import categories, load_investors, search_investors

st.set_page_config(page_title="Investor Research Library | Market Recon", page_icon="📚", layout="wide")
st.title("Investor Research Library")
st.caption("A curated index of historical investors, public learning resources, and primary-source starting points. Educational reference—not investment advice.")
st.warning("Investor profiles are not endorsements. Historical strategies and disclosed holdings do not predict future results.")

records = load_investors()
col1, col2 = st.columns([2, 1])
with col1:
    query = st.text_input("Search investor, strategy, or concept", placeholder="e.g. value, macro, diversification")
with col2:
    selected_category = st.selectbox("Strategy family", ["All"] + categories())

matches = search_investors(query, None if selected_category == "All" else selected_category)
st.caption(f"Showing {len(matches)} of {len(records)} profiles")
for investor in matches:
    with st.expander(f"{investor['name']} — {investor['category']}"):
        st.write(investor["strategy"])
        st.caption(investor["research_note"])
        st.markdown(f"[Open source / starting reference]({investor['source_url']}) · source type: {investor['source_type']}")

st.subheader("Research priorities")
st.markdown("Start with original shareholder letters, investor memos, books, interviews, and regulatory filings. For 13F context and limitations, see [the research collection notes](https://github.com/1243353366/Market-Recon/blob/main/data/investors/README.md).")
