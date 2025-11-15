import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ----------------------
# Streamlit: konfiguracja strony
# ----------------------
st.set_page_config(
    page_title="CryptoTrend.pl - Śledź trendy kryptowalut",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------
# Ukrycie menu Streamlit
# ----------------------
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
st.markdown("""
<script defer src="https://cloud.umami.is/script.js" data-website-id="c7d2a4c0-2ae9-406b-a38a-fdd313c83a1a"></script>
""", unsafe_allow_html=True)

# ----------------------
# Słownik popularnych kryptowalut
# ----------------------
kryptowaluty = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Tether (USDT)": "USDT-USD",
    "BNB (BNB)": "BNB-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP (XRP)": "XRP-USD",
    "Cardano (ADA)": "ADA-USD",
    "Dogecoin (DOGE)": "DOGE-USD",
    "Polygon (MATIC)": "MATIC-USD",
    "Polkadot (DOT)": "DOT-USD",
    "Litecoin (LTC)": "LTC-USD",
    "Shiba Inu (SHIB)": "SHIB-USD",
    "Avalanche (AVAX)": "AVAX-USD",
    "Chainlink (LINK)": "LINK-USD",
    "Uniswap (UNI)": "UNI-USD"
}

st.title("₿ CryptoTrend.pl")
st.write("Śledź trendy kryptowalut i podejmuj lepsze decyzje inwestycyjne.")

# ----------------------
# Wybór kryptowaluty
# ----------------------
st.subheader("🔍 Wybierz kryptowalutę")
wybrana = st.selectbox(
    "Najpopularniejsze kryptowaluty:",
    options=list(kryptowaluty.keys()),
    index=0
)
symbol = kryptowaluty[wybrana]

with st.expander("💡 Lub wpisz własny symbol"):
    st.caption("Wpisz symbol i naciśnij Enter")
    custom_symbol = st.text_input(
        "Symbol (format: XXX-USD):",
        placeholder="np. DOT-USD, AVAX-USD",
        help="Wpisz symbol kryptowaluty i naciśnij Enter aby zastosować",
        label_visibility="visible"
    )
    if custom_symbol:
        symbol = custom_symbol.upper()

# ----------------------
# Wybór zakresu dat
# ----------------------
col1, col2 = st.columns(2)
with col1:
    data_od = st.date_input(
        "Data od:",
        value=datetime.now() - timedelta(days=90),
        max_value=datetime.now()
    )
with col2:
    data_do = st.date_input(
        "Data do:",
        value=datetime.now(),
        max_value=datetime.now()
    )

# ----------------------
# Cache funkcji pobierania danych
# ----------------------
@st.cache_data
def pobierz_dane(symbol, start_str, end_str):
    df = yf.download(symbol, start=start_str, end=end_str, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={
        'Open': 'Otwarcie',
        'High': 'Maksimum',
        'Low': 'Minimum',
        'Close': 'Zamknięcie',
        'Volume': 'Wolumen'
    })
    df.index.name = 'Data'
    return df

# ----------------------
# Pobranie i wyświetlenie danych
# ----------------------
if symbol and data_od and data_do:
    if data_od >= data_do:
        st.error("Data początkowa musi być wcześniejsza niż data końcowa!")
    else:
        st.info(f"🔍 Wybrany zakres: {data_od.strftime('%d-%m-%Y')} → {data_do.strftime('%d-%m-%Y')}")
        start_str = data_od.strftime('%Y-%m-%d')
        end_str = (data_do + timedelta(days=1)).strftime('%Y-%m-%d')

        with st.spinner('Pobieram dane z Yahoo Finance...'):
            data = pobierz_dane(symbol, start_str, end_str)

        if not data.empty:
            st.subheader(f"Dane dla: {symbol}")
            st.success(f"✅ Pobrano {len(data)} dni notowań")
            st.write(f"📅 Pierwsza data: **{data.index.min().strftime('%d-%m-%Y')}**")
            st.write(f"📅 Ostatnia data: **{data.index.max().strftime('%d-%m-%Y')}**")
            st.dataframe(data, height=400)

            with st.expander("📊 Pokaż tylko ostatnie 10 notowań"):
                st.dataframe(data.tail(10))

            # ----------------------
            # Lazy loading wykresu
            # ----------------------
            if st.button("📈 Pokaż wykres cen zamknięcia"):
                with st.spinner("Tworzę wykres..."):
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Zamknięcie'],
                        mode='lines',
                        name='Cena zamknięcia',
                        line=dict(color='#636EFA', width=2),
                        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Cena: $%{y:.2f}<extra></extra>'
                    ))

                    fig.update_xaxes(
                        tickformat='%d %b %Y',
                        tickangle=-45,
                        dtick="M1" if len(data) > 365 else None
                    )

                    fig.update_layout(
                        title=f'Ceny zamknięcia {symbol}',
                        xaxis_title="Data",
                        yaxis_title="Cena (USD)",
                        hovermode='x unified',
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # ----------------------
            # Lazy loading średnich kroczących i trendu
            # ----------------------
            if len(data) >= 50:
                if st.button("📊 Pokaż średnie kroczące i trend"):
                    ma20 = data['Zamknięcie'].rolling(20).mean().iloc[-1]
                    ma50 = data['Zamknięcie'].rolling(50).mean().iloc[-1]
                    last = data['Zamknięcie'].iloc[-1]

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Aktualna cena", f"${last:.2f}")
                    col2.metric("Średnia 20 dni", f"${ma20:.2f}")
                    col3.metric("Średnia 50 dni", f"${ma50:.2f}")

                    if last > ma20 > ma50:
                        st.success("📈 Trend wzrostowy - cena powyżej obu średnich kroczących")
                    elif last < ma20 < ma50:
                        st.error("📉 Trend spadkowy - cena poniżej obu średnich kroczących")
                    else:
                        st.info("⚖️ Trend boczny - cena między średnimi kroczącymi")
            else:
                st.warning(f"⚠️ Za mało danych do obliczenia trendu (potrzeba minimum 50 dni, masz {len(data)} dni)")
        else:
            st.error(f"❌ Brak danych dla {symbol} w wybranym zakresie")
            st.write("- Możliwe przyczyny: nieprawidłowy symbol, brak danych historycznych, niepoprawny format XXX-USD")

st.divider()
st.caption("📊 CryptoTrend.pl - Analizuj trendy kryptowalut i podejmuj mądre decyzje inwestycyjne")
