import streamlit as st

st.set_page_config(
    page_title="CryptoTrend.pl - Sledz trendy kryptowalut",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

st.title("💰 CryptoTrend.pl")
st.write("Sledz trendy kryptowalut i podejmuj lepsze decyzje inwestycyjne.")

st.subheader("🔍 Wybierz kryptowalute")
wybrana = st.selectbox(
    "Najpopularniejsze kryptowaluty:",
    options=list(kryptowaluty.keys()),
    index=0
)
symbol = kryptowaluty[wybrana]

with st.expander("💡 Lub wpisz wlasny symbol"):
    st.caption("Wpisz symbol i nacisnij Enter")
    custom_symbol = st.text_input(
        "Symbol (format: XXX-USD):",
        placeholder="np. DOT-USD, AVAX-USD",
        help="Wpisz symbol kryptowaluty i nacisnij Enter aby zastosowac",
        label_visibility="visible"
    )
    if custom_symbol:
        symbol = custom_symbol.upper()

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

@st.cache_data
def pobierz_dane(symbol, start_str, end_str):
    df = yf.download(symbol, start=start_str, end=end_str, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={
        'Open': 'Otwarcie',
        'High': 'Maksimum',
        'Low': 'Minimum',
        'Close': 'Zamkniecie',
        'Volume': 'Wolumen'
    })
    df.index.name = 'Data'
    return df

if symbol and data_od and data_do:
    if data_od >= data_do:
        st.error("Data poczatkowa musi byc wczesniejsza niz data koncowa!")
    else:
        st.info(f"🔍 Wybrany zakres: {data_od.strftime('%d-%m-%Y')} → {data_do.strftime('%d-%m-%Y')}")
        start_str = data_od.strftime('%Y-%m-%d')
        end_str = (data_do + timedelta(days=1)).strftime('%Y-%m-%d')

        with st.spinner('Pobieram dane z Yahoo Finance...'):
            data = pobierz_dane(symbol, start_str, end_str)

        if not data.empty:
            st.subheader(f"Dane dla: {symbol}")
            st.success(f"✅ Pobrano {len(data)} dni notowan")
            st.write(f"📅 Pierwsza data: **{data.index.min().strftime('%d-%m-%Y')}**")
            st.write(f"📅 Ostatnia data: **{data.index.max().strftime('%d-%m-%Y')}**")
            st.dataframe(data, height=400)

            with st.expander("📊 Pokaz tylko ostatnie 10 notowan"):
                st.dataframe(data.tail(10))

            if st.button("📈 Pokaz wykres cen zamkniecia"):
                with st.spinner("Tworze wykres..."):
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data['Zamkniecie'],
                        mode='lines',
                        name='Cena zamkniecia',
                        line=dict(color='#636EFA', width=2),
                        hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Cena: $%{y:.2f}<extra></extra>'
                    ))

                    fig.update_xaxes(
                        tickformat='%d %b %Y',
                        tickangle=-45,
                        dtick="M1" if len(data) > 365 else None
                    )

                    fig.update_layout(
                        title=f'Ceny zamkniecia {symbol}',
                        xaxis_title="Data",
                        yaxis_title="Cena (USD)",
                        hovermode='x unified',
                        template='plotly_white'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if len(data) >= 50:
                if st.button("📊 Pokaz srednie kroczace i trend"):
                    ma20 = data['Zamkniecie'].rolling(20).mean().iloc[-1]
                    ma50 = data['Zamkniecie'].rolling(50).mean().iloc[-1]
                    last = data['Zamkniecie'].iloc[-1]

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Aktualna cena", f"${last:.2f}")
                    col2.metric("Srednia 20 dni", f"${ma20:.2f}")
                    col3.metric("Srednia 50 dni", f"${ma50:.2f}")

                    if last > ma20 > ma50:
                        st.success("📈 Trend wzrostowy - cena powyzej obu srednich kroczacych")
                    elif last < ma20 < ma50:
                        st.error("📉 Trend spadkowy - cena ponizej obu srednich kroczacych")
                    else:
                        st.info("⚖️ Trend boczny - cena miedzy srednimi kroczacymi")
            else:
                st.warning(f"⚠️ Za malo danych do obliczenia trendu (potrzeba minimum 50 dni, masz {len(data)} dni)")
        else:
            st.error(f"❌ Brak danych dla {symbol} w wybranym zakresie")
            st.write("- Mozliwe przyczyny: nieprawidlowy symbol, brak danych historycznych, niepoprawny format XXX-USD")

st.divider()
st.caption("📊 CryptoTrend.pl - Analizuj trendy kryptowalut i podejmuj madre decyzje inwestycyjne")
