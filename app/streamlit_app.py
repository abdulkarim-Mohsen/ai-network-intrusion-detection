"""Read-only Streamlit UI scaffold; actual dashboard is Phase 5."""

import streamlit as st

st.set_page_config(page_title="NIDS Research Dashboard", layout="wide")
st.title("AI-Based Network Intrusion Detection")
st.info(
    "Phase 1 scaffold only. No trained models, data, or measured evaluation "
    "results are available. The offline dashboard will be built in Phase 5."
)
st.caption("Defensive research only — this application performs no live network scanning.")
