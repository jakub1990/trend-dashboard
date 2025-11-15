import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="CryptoTrend.pl", page_icon="💰", layout="wide")

st.title("💰 CryptoTrend.pl")
st.write("Śledź trendy kryptowalut i podejmuj lepsze decyzje inwestycyjne")

kryptowaluty = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Solana (SOL)": "SOL-USD",
    "XRP (XRP)": "XRP-USD",
    "Cardano (ADA)": "ADA-USD",
    "Dogecoin (DOGE)": "DOGE-USD",
    "Polygon (MATIC)": "MATIC-USD",
    "Litecoin (LTC)": "LTC-USD"
}

wybrana = st.selectbox("Wybierz kryptowalutę:", list(kryptowaluty.keys()))
symbol = kryptowaluty[wybrana]

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
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return pd.DataFrame()

if st.button("Wczytaj dane", type="primary"):
    if data_od >= data_do:
        st.error("Data początkowa musi być wcześniejsza niż końcowa")
    else:
        with st.spinner("Pobieranie danych..."):
            dane = pobierz_dane(symbol, data_od, data_do)
            
            if not dane.empty and 'Close' in dane.columns:
                st.success(f"Wczytano {len(dane)} dni danych")
                
                zakladka1, zakladka2, zakladka3 = st.tabs(["Tabela danych", "Wykres cen", "Statystyki"])
                
                with zakladka1:
                    st.dataframe(dane, use_container_width=True)
                
                with zakladka2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dane.index,
                        y=dane['Close'],
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
                        cena_aktualna = float(dane['Close'].iloc[-1])
                        cena_najwyzsza = float(dane['High'].max())
                        cena_najnizsza = float(dane['Low'].min())
                        cena_srednia = float(dane['Close'].mean())
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Cena aktualna", f"${cena_aktualna:.2f}")
                        col2.metric("Najwyższa", f"${cena_najwyzsza:.2f}")
                        col3.metric("Najniższa", f"${cena_najnizsza:.2f}")
                        col4.metric("Średnia", f"${cena_srednia:.2f}")
                        
                        if len(dane) >= 50:
                            ma20 = float(dane['Close'].rolling(20).mean().iloc[-1])
                            ma50 = float(dane['Close'].rolling(50).mean().iloc[-1])
                            
                            st.subheader("Analiza trendu")
                            col1, col2 = st.columns(2)
                            col1.metric("Średnia krocząca 20-dniowa", f"${ma20:.2f}")
                            col2.metric("Średnia krocząca 50-dniowa", f"${ma50:.2f}")
                            
                            if cena_aktualna > ma20 > ma50:
                                st.success("Silny trend wzrostowy - cena powyżej obu średnich kroczących")
                            elif cena_aktualna < ma20 < ma50:
                                st.error("Silny trend spadkowy - cena poniżej obu średnich kroczących")
                            else:
                                st.info("Trend boczny - mieszane sygnały")
                        else:
                            st.warning(f"Za mało danych do analizy trendu (potrzeba minimum 50 dni, masz {len(dane)} dni)")
                    except Exception as e:
                        st.error(f"Błąd obliczania statystyk: {e}")
            else:
                st.error("Brak danych dla wybranego okresu")

st.divider()
st.caption("CryptoTrend.pl - Panel analizy trendów kryptowalut")
