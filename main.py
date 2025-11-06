import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trend Dashboard", page_icon="📊")

st.title("📊 Trend Dashboard")
st.write("Sprawdź trendy akcji lub kryptowalut w prosty sposób.")

symbol = st.text_input("Podaj symbol (np. AAPL, BTC-USD):", "AAPL")

if symbol:
    data = yf.download(symbol, period="3mo", interval="1d", group_by='ticker')
    if not data.empty:
        st.subheader(f"Dane dla: {symbol}")
        st.write(data.tail())

        fig = px.line(data, x=data.index, y='Close', title=f'Ceny zamknięcia {symbol}')
        st.plotly_chart(fig)

        # Obliczenia trendu
        ma20 = data['Close'].rolling(20).mean().iloc[-1]
        ma50 = data['Close'].rolling(50).mean().iloc[-1]
        last = data['Close'].iloc[-1]

        if last > ma20 > ma50:
            st.success("📈 Trend wzrostowy")
        elif last < ma20 < ma50:
            st.error("📉 Trend spadkowy")
        else:
            st.info("⚖️ Trend boczny")
    else:
        st.warning("Nie udało się pobrać danych — sprawdź symbol.")
