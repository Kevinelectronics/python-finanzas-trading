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

    # En este endpoint, los datos vienen en la clave "historical"
    historical = data.get("historical", [])

    df = pd.DataFrame(historical)

    # Convertimos la fecha a datetime para poder ordenar/filtrar fácilmente
    df["date"] = pd.to_datetime(df["date"])

    # Ordenamos de más antiguo a más reciente
    df = df.sort_values("date")

    # Nos quedamos con las columnas más útiles
    df = df[["date", "open", "high", "low", "close", "volume"]]

    # Ejemplo financiero simple: retorno diario (%)
    df["daily_return"] = df["close"].pct_change()

    return df


# -----------------------------
# 4) MÉTODOS ÚTILES (para enseñar en vídeo)
# -----------------------------
def explore_dataframe(df, name="DataFrame"):
    """
    Pequeña función para mostrar el checklist rápido de exploración.
    """
    print(f"\n===== {name} =====")
    #print("Shape (filas, columnas):", df.shape)
    print("\nColumnas:", list(df.columns))
    print("\nPrimeras filas:")
    print(df.head())

    print("\nInfo (tipos y nulos):")
    df.info()

    # describe solo funciona con columnas numéricas, ideal para ver rangos
    #print("\nDescribe (resumen numérico):")
    #print(df.describe(numeric_only=True))


# -----------------------------
# 5) MAIN
# -----------------------------
if __name__ == "__main__":
    # A) Quotes
    quotes_df = get_quotes_df(["AAPL", "MSFT", "TSLA"])
    explore_dataframe(quotes_df, "QUOTES (precio actual)")
    print(quotes_df)

    

    # Ejemplo de métodos útiles:
    # Ordenar por mayor cambio porcentual
    if "changesPercentage" in quotes_df.columns:
        sorted_df = quotes_df.sort_values("changesPercentage", ascending=False)
        print("\nOrdenado por changesPercentage:")
        print(sorted_df[["symbol", "price", "changesPercentage"]].head())

    # Filtrar solo acciones con precio > 100 (si existe la columna)
    if "price" in quotes_df.columns:
        filtered_df = quotes_df[quotes_df["price"] > 100]
        print("\nFiltrado: price > 100")
        print(filtered_df[["symbol", "price"]])

    # B) Historical
    hist_df = get_historical_df("AAPL", "2024-01-01", "2024-01-15")
    explore_dataframe(hist_df, "HISTÓRICOS (OHLCV)")

    # Guardar a CSV (útil para la siguiente clase)
    #hist_df.to_csv("AAPL_historical.csv", index=False)
    #print("\n✅ Guardado: AAPL_historical.csv")