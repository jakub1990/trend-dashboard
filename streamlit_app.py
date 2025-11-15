import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="CryptoTrend.pl", page_icon="💰", layout="wide")

st.title("💰 CryptoTrend.pl")
st.write("Track cryptocurrency trends and make better investment decisions")

cryptos = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP (XRP)": "XRP-USD",
    "Cardano (ADA)": "ADA-USD",
    "Dogecoin (DOGE)": "DOGE-USD",
    "Polygon (MATIC)": "MATIC-USD",
    "Litecoin (LTC)": "LTC-USD"
}

selected = st.selectbox("Select cryptocurrency:", list(cryptos.keys()))
symbol = cryptos[selected]

col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("From:", value=datetime.now() - timedelta(days=90))
with col2:
    date_to = st.date_input("To:", value=datetime.now())

@st.cache_data
def load_data(symbol, start, end):
    try:
        df = yf.download(symbol, start=start, end=end, progress=False)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

if st.button("Load Data", type="primary"):
    if date_from >= date_to:
        st.error("Start date must be before end date")
    else:
        with st.spinner("Loading data..."):
            data = load_data(symbol, date_from, date_to)
            
            if not data.empty:
                st.success(f"Loaded {len(data)} days of data")
                
                tab1, tab2, tab3 = st.tabs(["Data Table", "Price Chart", "Statistics"])
                
                with tab1:
                    st.dataframe(data, use_container_width=True)
                
                with tab2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Close'],
                        mode='lines',
                        name='Close Price',
                        line=dict(color='#00D4FF', width=2)
                    ))
                    fig.update_layout(
                        title=f"{symbol} Price History",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode='x unified',
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Current Price", f"${data['Close'].iloc[-1]:.2f}")
                    col2.metric("Highest", f"${data['High'].max():.2f}")
                    col3.metric("Lowest", f"${data['Low'].min():.2f}")
                    col4.metric("Average", f"${data['Close'].mean():.2f}")
                    
                    if len(data) >= 50:
                        ma20 = data['Close'].rolling(20).mean().iloc[-1]
                        ma50 = data['Close'].rolling(50).mean().iloc[-1]
                        current = data['Close'].iloc[-1]
                        
                        st.subheader("Trend Analysis")
                        col1, col2 = st.columns(2)
                        col1.metric("20-day Moving Average", f"${ma20:.2f}")
                        col2.metric("50-day Moving Average", f"${ma50:.2f}")
                        
                        if current > ma20 > ma50:
                            st.success("Strong Uptrend - Price above both moving averages")
                        elif current < ma20 < ma50:
                            st.error("Strong Downtrend - Price below both moving averages")
                        else:
                            st.info("Sideways Trend - Mixed signals")
            else:
                st.error("No data available for selected period")

st.divider()
st.caption("CryptoTrend.pl - Cryptocurrency trend analysis dashboard")
