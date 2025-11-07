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

if symbol:
    # Pobieranie danych w wybranym zakresie
    data = yf.download(symbol, start=data_od, end=data_do)

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
        st.write(f"Zakres: {data.index.min().strftime('%d-%m-%Y')} do {data.index.max().strftime('%d-%m-%Y')}")
        st.write(data.tail())

        # Wykres z polskimi nazwami miesięcy
        fig = px.line(data, x=data.index, y='Zamknięcie', title=f'Ceny zamknięcia {symbol}')

        # Formatowanie osi X z polskimi nazwami miesięcy
        fig.update_xaxes(
            tickformat='%d %b %Y',
            tickformatstops=[
                dict(dtickrange=[None, 86400000], value='%d %b'),  # dzień
                dict(dtickrange=[86400000, 2628000000], value='%d %b'),  # tydzień
                dict(dtickrange=[2628000000, None], value='%b %Y')  # miesiąc
            ]
        )

        # Zamiana angielskich nazw miesięcy na polskie
        polskie_miesiace = {
            'Jan': 'Sty', 'Feb': 'Lut', 'Mar': 'Mar', 'Apr': 'Kwi',
            'May': 'Maj', 'Jun': 'Cze', 'Jul': 'Lip', 'Aug': 'Sie',
            'Sep': 'Wrz', 'Oct': 'Paź', 'Nov': 'Lis', 'Dec': 'Gru'
        }

        fig.for_each_xaxis(lambda x: x.update(
            ticktext=[polskie_miesiace.get(t.split()[1], t.split()[1]) + ' ' + t.split()[0] if len(t.split()) > 1 else t 
                      for t in fig.layout.xaxis.ticktext] if fig.layout.xaxis.ticktext else None
        ))

        st.plotly_chart(fig)

        # Obliczenia trendu
        if len(data) >= 50:
            ma20 = data['Zamknięcie'].rolling(20).mean().iloc[-1]
            ma50 = data['Zamknięcie'].rolling(50).mean().iloc[-1]
            last = data['Zamknięcie'].iloc[-1]

            if last > ma20 > ma50:
                st.success("📈 Trend wzrostowy")
            elif last < ma20 < ma50:
                st.error("📉 Trend spadkowy")
            else:
                st.info("⚖️ Trend boczny")
        else:
            st.warning("Za mało danych do obliczenia trendu (potrzeba minimum 50 dni)")
    else:
        st.warning("Nie udało się pobrać danych — sprawdź symbol lub zakres dat.")