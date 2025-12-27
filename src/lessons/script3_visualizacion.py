import os
import requests
import pandas as pd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import mplfinance as mpf

# =========================
# 1) CONFIGURACIÓN
# =========================

load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")

BASE_URL = "https://financialmodelingprep.com/api/v3"


def get_ohlcv_df(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Descarga datos OHLCV (open, high, low, close, volume) desde FMP y devuelve un DataFrame
    listo para usar con mplfinance.

    - Índice: date (datetime)
    - Columnas: open, high, low, close, volume
    """
    if not API_KEY:
        raise ValueError("❌ No se encontró FMP_API_KEY. Revisa tu archivo .env (debe llamarse .env).")

    params = {"from": start_date, "to": end_date, "apikey": API_KEY}
    url = f"{BASE_URL}/historical-price-full/{symbol}"

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    payload = r.json()
    historical = payload.get("historical", [])

    if not historical:
        raise ValueError("❌ No se recibieron datos. Revisa el símbolo o el rango de fechas.")

    df = pd.DataFrame(historical)

    # Convertimos y dejamos el formato que espera mplfinance
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # Nos quedamos con OHLCV en el orden correcto
    df = df[["open", "high", "low", "close", "volume"]]

    return df


def add_financial_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade métricas típicas para visualización:
    - daily_return: retorno diario (% en decimal)
    - volatility_20: volatilidad rolling 20 días (std de retornos)
    - drawdown: caída desde máximos
    """
    df = df.copy()

    # Retorno diario: (Close_t / Close_{t-1}) - 1
    df["daily_return"] = df["close"].pct_change()

    # Volatilidad rolling 20 días (simple, didáctica)
    df["volatility_20"] = df["daily_return"].rolling(20).std()

    # Drawdown: diferencia entre el precio actual y el máximo histórico acumulado
    df["cum_max"] = df["close"].cummax()
    df["drawdown"] = (df["close"] - df["cum_max"]) / df["cum_max"]

    return df


def plot_candles_ohlcv(df: pd.DataFrame, symbol: str):
    """
    Gráfico OHLCV con velas + volumen + medias móviles usando mplfinance.
    """
    style = mpf.make_mpf_style(
        base_mpf_style="charles",
        rc={"font.size": 9}
    )

    mpf.plot(
        df,
        type="candle",
        volume=True,
        style=style,
        title=f"{symbol} – OHLCV (Velas + Volumen)",
        ylabel="Precio",
        ylabel_lower="Volumen",
        mav=(20, 50),  # Medias móviles simples
        figsize=(12, 6)
    )


def plot_daily_returns(df: pd.DataFrame, symbol: str):
    """
    Gráfico de retornos diarios.
    """
    returns = df["daily_return"].dropna()

    plt.figure(figsize=(12, 4))
    plt.plot(returns.index, returns.values)
    plt.title(f"{symbol} – Retornos diarios")
    plt.xlabel("Fecha")
    plt.ylabel("Retorno (decimal)")
    plt.tight_layout()
    plt.show()


def plot_rolling_volatility(df: pd.DataFrame, symbol: str):
    """
    Volatilidad rolling 20 días (std de retornos).
    """
    vol = df["volatility_20"].dropna()

    plt.figure(figsize=(12, 4))
    plt.plot(vol.index, vol.values)
    plt.title(f"{symbol} – Volatilidad rolling (20 días)")
    plt.xlabel("Fecha")
    plt.ylabel("Volatilidad (std)")
    plt.tight_layout()
    plt.show()


def plot_drawdown(df: pd.DataFrame, symbol: str):
    """
    Drawdown: caídas desde máximos acumulados.
    """
    dd = df["drawdown"].dropna()

    plt.figure(figsize=(12, 4))
    plt.plot(dd.index, dd.values)
    plt.title(f"{symbol} – Drawdown")
    plt.xlabel("Fecha")
    plt.ylabel("Drawdown (decimal)")
    plt.tight_layout()
    plt.show()


# =========================
# 2) MAIN (DEMO PARA LA CLASE)
# =========================

if __name__ == "__main__":
    SYMBOL = "AAPL"
    START = "2024-01-01"
    END = "2024-03-31"

    # 1) Descargar OHLCV
    df = get_ohlcv_df(SYMBOL, START, END)

    # 2) Añadir métricas financieras útiles (retornos, volatilidad, drawdown)
    df = add_financial_metrics(df)

    # 3) Gráfico pro: velas + volumen + MAs
    plot_candles_ohlcv(df, SYMBOL)

    # 4) Gráficos extra (muy útiles y fáciles de explicar)
    plot_daily_returns(df, SYMBOL)
    plot_rolling_volatility(df, SYMBOL)
    plot_drawdown(df, SYMBOL)

    # Extra: guardar CSV para siguientes clases (automatización / dashboard)
    df.to_csv(f"{SYMBOL}_ohlcv_with_metrics.csv")
    print(f"✅ Guardado: {SYMBOL}_ohlcv_with_metrics.csv")
