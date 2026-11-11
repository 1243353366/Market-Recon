from __future__ import annotations

import streamlit as st

from market_recon.coach.agent import InvestorContext, coach

st.set_page_config(page_title="Investing Coach | Market Recon", page_icon="🧭", layout="wide")
st.title("Educational Investing Coach")
st.caption("A bounded learning assistant for investing habits—not a financial adviser, stock picker, or trading agent.")
st.info("Do not enter account numbers, tax IDs, exact balances, passwords, or other sensitive personal information. Responses are general education and may be incomplete.")

with st.form("coach_form"):
    question = st.text_area("What investing concept would you like to understand?", placeholder="How do diversification and regular investing work?")
    col1, col2 = st.columns(2)
    with col1:
        horizon = st.selectbox("Broad time horizon (optional)", ["Prefer not to say", "Under 3 years", "3–10 years", "Over 10 years", "Unsure"])
        reserve = st.selectbox("Do you feel you have an emergency reserve? (optional)", ["Unsure / skip", "Yes", "No"])
    with col2:
        debt = st.selectbox("Are high-interest debts part of your current priorities? (optional)", ["Unsure / skip", "Yes", "No"])
        region = st.text_input("Country/region for official account-rule links (optional)", max_chars=60)
    submitted = st.form_submit_button("Get an educational coaching response")

if submitted:
    if not question.strip():
        st.warning("Enter a general investing question to continue.")
    else:
        context = InvestorContext(
            time_horizon="" if horizon in ("Prefer not to say", "Unsure") else horizon,
            emergency_reserve_ready={"Unsure / skip": None, "Yes": True, "No": False}[reserve],
            high_interest_debt={"Unsure / skip": None, "Yes": True, "No": False}[debt],
            country_or_region=region.strip(),
        )
        reply = coach(question, context)
        st.subheader("Learning response")
        st.markdown(reply.message)
        st.markdown(f"**A useful next step:** {reply.next_step}")
        st.caption(f"Workflow steps: {' → '.join(reply.tools_used)}")
        st.subheader("Sources to explore")
        for title, url in reply.sources:
            st.markdown(f"- [{title}]({url})")
        st.caption("The coach provides general education only. It does not recommend securities or allocations, or provide individualized investment, tax, or legal advice.")
