import streamlit as st
import pandas as pd
import requests
import sys
import os

# Ensure we can import the rebalancer module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'rebalancer')))
from engine import RebalanceEngine

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

# -------------------------------------------------------------------
# Data Fetching Logic
# -------------------------------------------------------------------
@st.cache_data(ttl=5) # Cache for 5 seconds to simulate real-time polling
def fetch_signals():
    try:
        # Connect to our API
        response = requests.get("http://localhost:8000/api/signals/latest")
        if response.status_code == 200:
            data = response.json().get('data', [])
            return pd.DataFrame(data)
    except requests.exceptions.ConnectionError:
        pass
    
    # Fallback to local CSV if API is offline
    try:
        return pd.read_csv("data/news_with_sentiment_and_impact.csv")
    except Exception:
        # Deep fallback for testing
        try:
            return pd.read_csv("../data/news_with_sentiment_and_impact.csv")
        except Exception:
            return pd.DataFrame()

# -------------------------------------------------------------------
# Dashboard Sections
# -------------------------------------------------------------------
df_signals = fetch_signals()

if df_signals.empty:
    st.error("❌ Failed to connect to Risk Engine API and no fallback data found.")
else:
    
    st.markdown("### 📡 Live Risk Signals Feed")
    
    # --- Metrics Cards ---
    col1, col2, col3 = st.columns(3)
    
    avg_sentiment = df_signals['sentiment_score'].mean()
    event_counts = df_signals['event_class'].value_counts()
    dominant_event = event_counts.idxmax() if not event_counts.empty else "None"
    high_impact_count = len(df_signals[df_signals['impact_score'] >= 7])
    
    with col1:
        st.metric("Avg Market Sentiment", f"{avg_sentiment:.2f}", 
                  delta="Bullish" if avg_sentiment > 0.1 else "Bearish" if avg_sentiment < -0.1 else "Neutral")
    with col2:
        st.metric("Dominant Event Theme", dominant_event)
    with col3:
        st.metric("High Impact Alerts (>=7)", high_impact_count, 
                  delta=f"{high_impact_count} Critical" if high_impact_count > 0 else "Normal",
                  delta_color="inverse")
                  
    if high_impact_count > 0:
        st.error(f"⚠️ High Impact Risk Detected! {high_impact_count} signal(s) exceeding severity threshold 7.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Format the dataframe for better UI presentation
    display_df = df_signals[['text', 'sentiment_label', 'sentiment_score', 'event_class', 'impact_score']].copy()
    
    # Apply some styling based on sentiment
    def color_sentiment(val):
        if val == 'positive':
            return 'color: #10B981; font-weight: bold;'
        elif val == 'negative':
            return 'color: #EF4444; font-weight: bold;'
        return 'color: #6B7280;'
        
    st.dataframe(
        display_df.style.applymap(color_sentiment, subset=['sentiment_label']),
        use_container_width=True,
        hide_index=True

    
    st.markdown("---")
    st.markdown("### ⚖️ Tactical Portfolio Rebalancing")
    
    # Run the Rebalancer Engine
    with st.spinner("Executing Rebalancing Algorithm..."):
        rebalancer = RebalanceEngine()
        # Mocking the client signals with what we fetched for the UI
        rebalancer.client.fetch_latest_signals = lambda: df_signals.to_dict(orient="records")
        updated_portfolio_df = rebalancer.execute_rebalance()
    
    # Display the Chart
    chart_data = updated_portfolio_df[['ticker', 'current_weight']].set_index('ticker')
    st.bar_chart(chart_data)
    
    # Display Transaction Log
    if rebalancer.transaction_log:
        st.markdown("#### 📜 Transaction History")
        st.dataframe(pd.DataFrame(rebalancer.transaction_log), use_container_width=True)
    else:
        st.info("No rebalancing transactions required at this time.")
