import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-LVHMK6XJJR"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-LVHMK6XJJR');
</script>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Trend Dashboard", page_icon="📊")

st.title("📊 Trend Dashboard")
st.write("Sprawdź trendy akcji lub kryptowalut w prosty sposób.")

symbol = st.text_input("Podaj symbol (np. AAPL, BTC-USD):", "AAPL")

# Wybór zakresu dat
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

# Funkcja do zamiany nazw miesięcy na polskie
def zamien_na_polskie(data_tekst):
    miesiace = {
        'Jan': 'Sty', 'Feb': 'Lut', 'Mar': 'Mar', 'Apr': 'Kwi',
        'May': 'Maj', 'Jun': 'Cze', 'Jul': 'Lip', 'Aug': 'Sie',
        'Sep': 'Wrz', 'Oct': 'Paź', 'Nov': 'Lis', 'Dec': 'Gru'
    }
    for ang, pol in miesiace.items():
        data_tekst = data_tekst.replace(ang, pol)
    return data_tekst

if symbol and data_od and data_do:
    if data_od >= data_do:
        st.error("Data początkowa musi być wcześniejsza niż data końcowa!")
    else:
        # Wyświetl wybrane daty
        st.info(f"🔍 Wybrany zakres: {data_od.strftime('%d-%m-%Y')} → {data_do.strftime('%d-%m-%Y')}")

        # Pobieranie danych w wybranym zakresie
        with st.spinner('Pobieram dane z Yahoo Finance...'):
            start_str = data_od.strftime('%Y-%m-%d')
            end_str = (data_do + timedelta(days=1)).strftime('%Y-%m-%d')

            data = yf.download(symbol, start=start_str, end=end_str, progress=False, auto_adjust=True)

        # Spłaszczenie kolumn MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Zmiana nazw kolumn na polskie
        data = data.rename(columns={
            'Open': 'Otwarcie',
            'High': 'Maksimum',
            'Low': 'Minimum',
            'Close': 'Zamknięcie',
            'Volume': 'Wolumen'
        })
        data.index.name = 'Data'

        if not data.empty:
            st.subheader(f"Dane dla: {symbol}")

            # Wyświetl faktyczny zakres pobranych danych
            rzeczywisty_od = data.index.min().strftime('%d-%m-%Y')
            rzeczywisty_do = data.index.max().strftime('%d-%m-%Y')

            st.success(f"✅ Pobrano {len(data)} dni notowań")
            st.write(f"📅 Pierwsza data: **{rzeczywisty_od}**")
            st.write(f"📅 Ostatnia data: **{rzeczywisty_do}**")

            # Tabelka - WSZYSTKIE dane z możliwością przewijania
            st.write("**Wszystkie notowania (można przewijać i sortować):**")
            st.dataframe(data, height=400, width='stretch')

            # Opcjonalnie: pokaż też ostatnie 10 wpisów wyraźnie
            with st.expander("📊 Pokaż tylko ostatnie 10 notowań"):
                st.dataframe(data.tail(10), width='stretch')

            # Wykres z polskimi miesiącami używając graph_objects
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Zamknięcie'],
                mode='lines',
                name='Cena zamknięcia',
                line=dict(color='#636EFA', width=2),
                hovertemplate='<b>%{x|%d-%m-%Y}</b><br>Cena: $%{y:.2f}<extra></extra>'
            ))

            # Ustawienie polskich nazw miesięcy na osi X
            fig.update_xaxes(
                tickformat='%d %b %Y',
                tickangle=-45,
                dtick="M1" if len(data) > 365 else None  # Pokaż co miesiąc jeśli więcej niż rok danych
            )

            # Zamiana nazw miesięcy na polskie
            fig.update_layout(
                title=f'Ceny zamknięcia {symbol}',
                xaxis_title="Data",
                yaxis_title="Cena (USD)",
                hovermode='x unified',
                template='plotly_white'
            )

            # Używamy JavaScript do zamiany nazw miesięcy
            fig.update_xaxes(ticktext=[
                zamien_na_polskie(d.strftime('%d %b %Y')) for d in pd.date_range(
                    start=data.index.min(), 
                    end=data.index.max(), 
                    freq='MS' if len(data) > 365 else '7D'
                )
            ], tickvals=pd.date_range(
                start=data.index.min(), 
                end=data.index.max(), 
                freq='MS' if len(data) > 365 else '7D'
            ))

            st.plotly_chart(fig, width='stretch')

            # Obliczenia trendu
            if len(data) >= 50:
                ma20 = data['Zamknięcie'].rolling(20).mean().iloc[-1]
                ma50 = data['Zamknięcie'].rolling(50).mean().iloc[-1]
                last = data['Zamknięcie'].iloc[-1]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Aktualna cena", f"${last:.2f}")
                with col2:
                    st.metric("Średnia 20 dni", f"${ma20:.2f}")
                with col3:
                    st.metric("Średnia 50 dni", f"${ma50:.2f}")

                if last > ma20 > ma50:
                    st.success("📈 Trend wzrostowy - cena powyżej obu średnich kroczących")
                elif last < ma20 < ma50:
                    st.error("📉 Trend spadkowy - cena poniżej obu średnich kroczących")
                else:
                    st.info("⚖️ Trend boczny - cena między średnimi kroczącymi")
            else:
                st.warning(f"⚠️ Za mało danych do obliczenia trendu (potrzeba minimum 50 dni, masz {len(data)} dni)")
        else:
            st.error(f"❌ Brak danych dla {symbol} w zakresie {data_od.strftime('%d-%m-%Y')} - {data_do.strftime('%d-%m-%Y')}")
            st.write("Możliwe przyczyny:")
            st.write("- Nieprawidłowy symbol")
            st.write("- Giełda była zamknięta w całym wybranym okresie")
            st.write("- Brak historycznych danych dla tego symbolu")
