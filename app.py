import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Aksje- og Signalsøk", layout="wide")

st.title("📈 Aksje- og Fondsanalyse Dashboard")
st.write("Følg med på markedsutvikling, tekniske indikatorer og kjøps-/salgssignaler i sanntid.")

st.sidebar.header("Innstillinger")
ticker = st.sidebar.text_input("Ticker-symbol (f.eks. EQNR.OL, AAPL, MSFT)", value="EQNR.OL")
periode = st.sidebar.selectbox("Periode", ["6mo", "1y", "2y", "5y"], index=1)
fast_sma = st.sidebar.slider("Kort SMA (Dager)", min_value=5, max_value=50, value=20)
slow_sma = st.sidebar.slider("Lang SMA (Dager)", min_value=20, max_value=200, value=50)

@st.cache_data
def hent_data(symbol, period):
    df = yf.Ticker(symbol).history(period=period)
    return df

data = hent_data(ticker, periode)

if data.empty:
    st.error(f"Fant ingen data for '{ticker}'. Sjekk om tickeren er riktig formatert.")
else:
    data['SMA_Fast'] = data['Close'].rolling(window=fast_sma).mean()
    data['SMA_Slow'] = data['Close'].rolling(window=slow_sma).mean()

    data['Signal'] = data['SMA_Fast'] > data['SMA_Slow']
    data['Position_Change'] = data['Signal'].astype(int).diff()

    siste_pris = data['Close'].iloc[-1]
    forrige_pris = data['Close'].iloc[-2]
    endring = siste_pris - forrige_pris
    prosent_endring = (endring / forrige_pris) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Siste Sluttkurs", f"{siste_pris:.2f}", f"{prosent_endring:.2f}%")
    col2.metric(f"Kort SMA ({fast_sma}d)", f"{data['SMA_Fast'].iloc[-1]:.2f}")
    col3.metric(f"Lang SMA ({slow_sma}d)", f"{data['SMA_Slow'].iloc[-1]:.2f}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Aksjekurs', line=dict(color='gray', width=1.5)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Fast'], name=f'SMA {fast_sma}', line=dict(color='green', width=1)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Slow'], name=f'SMA {slow_sma}', line=dict(color='red', width=1)))

    kjop = data[data['Position_Change'] == 1]
    salg = data[data['Position_Change'] == -1]

    fig.add_trace(go.Scatter(x=kjop.index, y=kjop['Close'], mode='markers', name='Kjøpssignal', marker=dict(symbol='triangle-up', size=14, color='green')))
    fig.add_trace(go.Scatter(x=salg.index, y=salg['Close'], mode='markers', name='Salgssignal', marker=dict(symbol='triangle-down', size=14, color='red')))

    fig.update_layout(title=f"Teknisk Analyse & Signaler for {ticker}", xaxis_title="Dato", yaxis_title="Pris", template="plotly_white", height=600)
    st.plotly_chart(fig, use_container_width=True)
