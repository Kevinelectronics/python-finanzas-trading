import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from datetime import date
import plotly.graph_objects as go

# ======================
# CONFIG
# ======================
load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3"

st.set_page_config(page_title="Dashboard Financiero", layout="wide")
st.title("📊 Dashboard Financiero Interactivo (Python + APIs)")

if not API_KEY:
    st.error("❌ No se encontró FMP_API_KEY. Revisa tu archivo .env")
    st.stop()


# ======================
# FUNCIONES
# ======================
def get_ohlcv(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Descarga OHLCV desde la API y devuelve DataFrame."""
    params = {"from": start_date, "to": end_date, "apikey": API_KEY}
    url = f"{BASE_URL}/historical-price-full/{symbol}"

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    historical = r.json().get("historical", [])
    if not historical:
        return pd.DataFrame()

    df = pd.DataFrame(historical)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df[["date", "open", "high", "low", "close", "volume"]]


def add_basic_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Añade SMA 20/50, retorno, volatilidad 20d y drawdown."""
    df = df.copy()
    df["return"] = df["close"].pct_change()
    df["sma_20"] = df["close"].rolling(20).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["volatility_20"] = df["return"].rolling(20).std()
    df["cum_max"] = df["close"].cummax()
    df["drawdown"] = (df["close"] - df["cum_max"]) / df["cum_max"]
    return df


def build_chart(df: pd.DataFrame, symbol: str, show_volume: bool) -> go.Figure:
    """Crea velas interactivas + medias móviles + (opcional) volumen."""
    fig = go.Figure()

    # Velas (OHLC)
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="OHLC",
        )
    )

    # Medias móviles
    fig.add_trace(go.Scatter(x=df["date"], y=df["sma_20"], mode="lines", name="SMA 20"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["sma_50"], mode="lines", name="SMA 50"))

    # Volumen (segundo eje)
    if show_volume:
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["volume"],
                name="Volumen",
                yaxis="y2",
                opacity=0.3,
            )
        )
        fig.update_layout(
            yaxis2=dict(
                title="Volumen",
                overlaying="y",
                side="right",
                showgrid=False,
            )
        )

    fig.update_layout(
        title=f"{symbol} — OHLCV Interactivo",
        xaxis_title="Fecha",
        yaxis_title="Precio",
        xaxis_rangeslider_visible=False,
        height=650,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


# ======================
# SIDEBAR
# ======================
st.sidebar.header("⚙️ Parámetros")

symbol = st.sidebar.selectbox("Activo", ["AAPL", "MSFT", "TSLA", "NVDA"])
start = st.sidebar.date_input("Fecha inicio", date(2024, 1, 1))
end = st.sidebar.date_input("Fecha fin", date.today())

show_volume = st.sidebar.checkbox("Mostrar volumen", value=True)

# ======================
# MAIN
# ======================
df = get_ohlcv(symbol, str(start), str(end))

if df.empty:
    st.warning("No se recibieron datos para ese rango/activo. Prueba otras fechas o símbolo.")
    st.stop()

df = add_basic_metrics(df)

# KPIs
last_price = df["close"].iloc[-1]
total_return = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
max_drawdown = df["drawdown"].min() * 100
vol_20 = df["volatility_20"].iloc[-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Precio actual", f"${last_price:.2f}")
c2.metric("Retorno total", f"{total_return:.2f}%")
c3.metric("Volatilidad (20d)", f"{vol_20:.4f}" if pd.notna(vol_20) else "—")
c4.metric("Drawdown máx", f"{max_drawdown:.2f}%")

st.divider()

# Gráfico interactivo
fig = build_chart(df, symbol, show_volume)
st.plotly_chart(fig, use_container_width=True)

# Tabla
with st.expander("📄 Ver últimos datos"):
    st.dataframe(df.tail(50), use_container_width=True)
