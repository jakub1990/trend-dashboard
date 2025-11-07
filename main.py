import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

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

if symbol and data_od and data_do:
    if data_od >= data_do:
        st.error("Data początkowa musi być wcześniejsza niż data końcowa!")
    else:
        # Wyświetl wybrane daty - to pokazuje co WYBRAŁEŚ
        st.info(f"🔍 Wybrany zakres: {data_od.strftime('%d-%m-%Y')} → {data_do.strftime('%d-%m-%Y')}")

        # Pobieranie danych w wybranym zakresie - BEZ CACHE
        with st.spinner('Pobieram dane z Yahoo Finance...'):
            # Konwertuj na string aby uniknąć problemów
            start_str = data_od.strftime('%Y-%m-%d')
            end_str = (data_do + timedelta(days=1)).strftime('%Y-%m-%d')  # +1 dzień bo end jest exclusive

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

            # Wyświetl faktyczny zakres pobranych danych - to pokazuje co FAKTYCZNIE pobrano
            rzeczywisty_od = data.index.min().strftime('%d-%m-%Y')
            rzeczywisty_do = data.index.max().strftime('%d-%m-%Y')

            st.success(f"✅ Pobrano {len(data)} dni notowań")
            st.write(f"📅 Pierwsza data: **{rzeczywisty_od}**")
            st.write(f"📅 Ostatnia data: **{rzeczywisty_do}**")

            # Tabelka - pokaż WSZYSTKIE dane jeśli mało, lub ostatnie 15
            st.write(f"**{'Wszystkie' if len(data) <= 15 else 'Ostatnie 15'} notowań:**")
            st.dataframe(data.tail(15) if len(data) > 15 else data, width='stretch')

            # Wykres
            fig = px.line(data, x=data.index, y='Zamknięcie', title=f'Ceny zamknięcia {symbol}')

            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Cena (USD)",
                hovermode='x unified'
            )

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
            st.write("- Giełda była zamknięta w całym wybranym okresie (weekendy/święta)")
            st.write("- Brak historycznych danych dla tego symbolu")