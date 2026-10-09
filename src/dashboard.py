import streamlit as st
import pandas as pd
import requests

# -------------------------------------------------------------------
# Page Configuration & Styling
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Risk Engine | Module A",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design Aesthetic
st.markdown("""
<style>
    .main-title {
        font-family: 'Inter', sans-serif;
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        font-family: 'Inter', sans-serif;
        color: #64748B;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Sidebar Configuration
# -------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/S%26P_Global_logo.svg/512px-S%26P_Global_logo.svg.png", width=150)
    st.markdown("---")
    st.header("⚙️ Control Panel")
    
    st.markdown("**API Status:**")
    st.success("🟢 Online")
    
    st.markdown("---")
    st.markdown("### Hackathon 2026")
    st.caption("Module A: Tactical Index Rebalancing")

# -------------------------------------------------------------------
# Main Dashboard Layout
# -------------------------------------------------------------------
st.markdown('<h1 class="main-title">Unified AI/NLP Risk Engine</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Real-time Financial Risk Signals & Tactical Portfolio Rebalancing</p>', unsafe_allow_html=True)

st.markdown("---")
st.info("Waiting for data stream to initialize...", icon="⏳")
