import streamlit as st

st.set_page_config(
    page_title="CryptoTrend.pl",
    page_icon="💰",
    layout="wide"
)

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

kryptowaluty = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP (XRP)": "XRP-USD",
    "Cardano (ADA)": "ADA-USD"
}

st.title("CryptoTrend.pl")
st.write("Track cryptocurrency trends")

wybrana = st.selectbox("Select:", list(kryptowaluty.keys()))
symbol = kryptowaluty[wybrana]

col1, col2 = st.columns(2)
with col1:
    data_od = st.date_input("From:", value=datetime.now() - timedelta(days=30))
with col2:
    data_do = st.date_input("To:", value=datetime.now())

@st.cache_data
def get_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end, progress=False)
    return df

if st.button("Load Data"):
    with st.spinner('Loading...'):
        data = get_data(symbol, data_od, data_do)
        if not data.empty:
            st.success(f"Loaded {len(data)} days")
            st.dataframe(data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines'))
            fig.update_layout(title=f'{symbol} Price', xaxis_title="Date", yaxis_title="Price USD")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data")
