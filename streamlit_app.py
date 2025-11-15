import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="CryptoTrend.pl", page_icon="💰", layout="wide")

st.title("💰 CryptoTrend.pl")
st.write("Śledź trendy kryptowalut i podejmuj lepsze decyzje inwestycyjne")

# Podstawowe popularne kryptowaluty
popularne_kryptowaluty = {
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
    "Uniswap (UNI)": "UNI-USD",
    "Cosmos (ATOM)": "ATOM-USD",
    "Ethereum Classic (ETC)": "ETC-USD",
    "Stellar (XLM)": "XLM-USD",
    "Monero (XMR)": "XMR-USD",
    "Algorand (ALGO)": "ALGO-USD",
    "VeChain (VET)": "VET-USD",
    "TRON (TRX)": "TRX-USD",
    "Internet Computer (ICP)": "ICP-USD",
    "Filecoin (FIL)": "FIL-USD",
    "Aptos (APT)": "APT-USD",
    "Arbitrum (ARB)": "ARB-USD",
    "Optimism (OP)": "OP-USD",
    "Near Protocol (NEAR)": "NEAR-USD",
    "Sui (SUI)": "SUI-USD",
    "Injective (INJ)": "INJ-USD"
}

st.subheader("🔍 Wyszukaj kryptowalutę")

# Wybór: popularna lista lub własny symbol
tryb = st.radio(
    "Sposób wyszukiwania:",
    ["📋 Wybierz z popularnych", "✍️ Wpisz własny symbol"],
    horizontal=True
)

symbol = None

if tryb == "📋 Wybierz z popularnych":
    wybrana = st.selectbox("Wybierz kryptowalutę:", list(popularne_kryptowaluty.keys()))
    symbol = popularne_kryptowaluty[wybrana]
    st.info(f"Symbol: **{symbol}**")
else:
    st.write("Wpisz symbol kryptowaluty (np. BTC, ETH, SOL)")
    col_a, col_b = st.columns([3, 1])
    
    with col_a:
        wlasny_symbol = st.text_input(
            "Symbol kryptowaluty:",
            placeholder="np. BTC, ETH, SOL, PEPE...",
            help="Wpisz skrót kryptowaluty bez '-USD'"
        ).upper().strip()
    
    with col_b:
        st.write("")
        st.write("")
        if st.button("🔍 Sprawdź", type="secondary"):
            if wlasny_symbol:
                with st.spinner(f"Sprawdzam czy {wlasny_symbol}-USD istnieje..."):
                    test_symbol = f"{wlasny_symbol}-USD"
                    try:
                        test_data = yf.Ticker(test_symbol)
                        info = test_data.info
                        
                        # Sprawdź czy dane są dostępne
                        if info and len(info) > 1 and 'symbol' in info:
                            st.success(f"✅ Znaleziono: **{wlasny_symbol}**")
                            if 'longName' in info:
                                st.write(f"Nazwa: {info['longName']}")
                        else:
                            st.error(f"❌ Nie znaleziono kryptowaluty: **{wlasny_symbol}**")
                            st.write("Spróbuj innego symbolu lub wybierz z listy popularnych.")
                    except Exception as e:
                        st.error(f"❌ Nie znaleziono kryptowaluty: **{wlasny_symbol}**")
                        st.write("Spróbuj innego symbolu lub wybierz z listy popularnych.")
    
    if wlasny_symbol:
        symbol = f"{wlasny_symbol}-USD"
        st.info(f"Symbol do wczytania: **{symbol}**")

st.divider()

col1, col2 = st.columns(2)
with col1:
    data_od = st.date_input("Od:", value=datetime.now() - timedelta(days=90))
with col2:
    data_do = st.date_input("Do:", value=datetime.now())

@st.cache_data
def pobierz_dane(symbol, start, end):
    try:
        df = yf.download(symbol, start=start, end=end, progress=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        df = df.rename(columns={
            'Open': 'Otwarcie',
            'High': 'Najwyższa',
            'Low': 'Najniższa',
            'Close': 'Zamknięcie',
            'Volume': 'Wolumen',
            'Adj Close': 'Zamknięcie skorygowane'
        })
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return pd.DataFrame()

if symbol and st.button("📥 Wczytaj dane", type="primary"):
    if data_od >= data_do:
        st.error("Data początkowa musi być wcześniejsza niż końcowa")
    else:
        with st.spinner("Pobieranie danych..."):
            dane = pobierz_dane(symbol, data_od, data_do)
            
            if not dane.empty and 'Zamknięcie' in dane.columns:
                st.success(f"✅ Wczytano {len(dane)} dni danych dla {symbol}")
                
                zakladka1, zakladka2, zakladka3 = st.tabs(["📊 Tabela danych", "📈 Wykres cen", "📉 Statystyki"])
                
                with zakladka1:
                    st.dataframe(dane, use_container_width=True)
                
                with zakladka2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dane.index,
                        y=dane['Zamknięcie'],
                        mode='lines',
                        name='Cena zamknięcia',
                        line=dict(color='#00D4FF', width=2)
                    ))
                    fig.update_layout(
                        title=f"Historia cen {symbol}",
                        xaxis_title="Data",
                        yaxis_title="Cena (USD)",
                        hovermode='x unified',
                        template='plotly_dark'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with zakladka3:
                    try:
                        cena_aktualna = float(dane['Zamknięcie'].iloc[-1])
                        cena_najwyzsza = float(dane['Najwyższa'].max())
                        cena_najnizsza = float(dane['Najniższa'].min())
                        cena_srednia = float(dane['Zamknięcie'].mean())
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Cena aktualna", f"${cena_aktualna:.2f}")
                        col2.metric("Najwyższa", f"${cena_najwyzsza:.2f}")
                        col3.metric("Najniższa", f"${cena_najnizsza:.2f}")
                        col4.metric("Średnia", f"${cena_srednia:.2f}")
                        
                        if len(dane) >= 50:
                            ma20 = float(dane['Zamknięcie'].rolling(20).mean().iloc[-1])
                            ma50 = float(dane['Zamknięcie'].rolling(50).mean().iloc[-1])
                            
                            st.subheader("Analiza trendu")
                            col1, col2 = st.columns(2)
                            col1.metric("Średnia krocząca 20-dniowa", f"${ma20:.2f}")
                            col2.metric("Średnia krocząca 50-dniowa", f"${ma50:.2f}")
                            
                            if cena_aktualna > ma20 > ma50:
                                st.success("🚀 Silny trend wzrostowy - cena powyżej obu średnich kroczących")
                            elif cena_aktualna < ma20 < ma50:
                                st.error("📉 Silny trend spadkowy - cena poniżej obu średnich kroczących")
                            else:
                                st.info("↔️ Trend boczny - mieszane sygnały")
                        else:
                            st.warning(f"⚠️ Za mało danych do analizy trendu (potrzeba minimum 50 dni, masz {len(dane)} dni)")
                    except Exception as e:
                        st.error(f"Błąd obliczania statystyk: {e}")
            else:
                st.error(f"❌ Brak danych dla {symbol} w wybranym okresie. Sprawdź czy symbol jest poprawny.")

st.divider()
st.caption("CryptoTrend.pl - Panel analizy trendów kryptowalut")
st.caption("💡 Wskazówka: Możesz wpisać dowolny symbol kryptowaluty dostępny na Yahoo Finance (np. PEPE, BONK, WIF)")
