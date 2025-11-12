import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, timedelta

# ----------------------
# Streamlit: konfiguracja strony i ukrycie menu/stopki
# ----------------------
st.set_page_config(
    page_title="CryptoTrend.pl - Śledź trendy kryptowalut",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <head>
        <title>CryptoTrend.pl - Śledź trendy kryptowalut</title>
        <meta name="description" content="CryptoTrend.pl pozwala śledzić ceny i trendy kryptowalut w czasie rzeczywistym, analizować wykresy i podejmować lepsze decyzje inwestycyjne.">
        <meta name="robots" content="index, follow">
        <link rel="icon" href="https://cryptotrend.pl/favicon.ico" type="image/x-icon">
        <meta property="og:title" content="CryptoTrend.pl">
        <meta property="og:description" content="Śledź ceny i trendy kryptowalut w czasie rzeczywistym.">
        <meta property="og:type" content="website">
    </head>
""", unsafe_allow_html=True)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----------------------
# Umami Analytics
# ----------------------
st.components.v1.html("""
<script defer src="https://cloud.umami.is/script.js" data-website-id="c7d2a4c0-2ae9-406b-a38a-fdd313c83a1a"></script>
""", he
