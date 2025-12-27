import os
import requests
import pandas as pd
from dotenv import load_dotenv

# 1) Cargar API key desde .env
load_dotenv()
API_KEY = os.getenv("FMP_API_KEY")

BASE_URL = "https://financialmodelingprep.com/api/v3"


def call_fmp(endpoint, params=None):
    """
    Llama a cualquier endpoint de FMP y devuelve JSON.
    """
    if params is None:
        params = {}

    params["apikey"] = API_KEY
    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


# -----------------------------
# 2) EJEMPLO A: QUOTES -> DataFrame (precio actual)
# -----------------------------
def get_quotes_df(symbols):
    """
    Obtiene precios actuales para una lista de símbolos y devuelve un DataFrame.
    """
    symbols_str = ",".join(symbols)
    data = call_fmp(f"quote/{symbols_str}")

    # Como data es una lista de diccionarios, pandas lo convierte directamente
    df = pd.DataFrame(data)

    return df


# -----------------------------
# 3) EJEMPLO B: HISTÓRICOS -> DataFrame (OHLCV)
# -----------------------------
def get_historical_df(symbol, start_date, end_date):
    """
    Obtiene precios históricos de un símbolo y devuelve un DataFrame OHLCV.
    """
    params = {"from": start_date, "to": end_date}
    data = call_fmp(f"historical-price-full/{symbol}", params=params)
    historical = data.get("historical", [])
    df = pd.DataFrame(historical)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df[["date", "open", "high", "low", "close", "volume"]]

    # Ejemplo financiero simple: retorno diario (%)
    df["daily_return"] = df["close"].pct_change()
    return df

hist_df = get_historical_df("AAPL", "2025-01-01", "2025-01-15")
print(hist_df)
#explore_dataframe(hist_df, "HISTÓRICOS (OHLCV)")