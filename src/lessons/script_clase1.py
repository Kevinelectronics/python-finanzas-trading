import requests
import os
from dotenv import load_dotenv
load_dotenv()  # ahora SÍ encuentra el archivo .env
# Cargamos la API key desde el archivo .env
API_KEY = os.getenv("FMP_API_KEY")

print(API_KEY)  # solo para comprobar en clase (luego se quita)


BASE_URL = "https://financialmodelingprep.com/api/v3"

def get_market_data(endpoint, params=None):
    """
    Llama a un endpoint de Market Data (Quote, Batch, etc.)
    """
    if params is None:
        params = {}

    params["apikey"] = API_KEY
    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

def get_stock_quote(symbol):
    """
    Obtiene el precio actual de una acción.
    """
    data = get_market_data(f"quote/{symbol}")
    return data[0]  # FMP devuelve una lista con un elemento



quote = get_stock_quote("AAPL")
print(quote)

print("Symbol:", quote["symbol"])
print("Price:", quote["price"])
print("Change %:", quote["changesPercentage"])
print(quote["earningsAnnouncement"])
