# -*- coding: utf-8 -*-
"""
bot_fmp_alpaca_paper.py
Bot sencillo: FMP (datos) -> señal SMA crossover -> Alpaca (paper trading)

Requisitos:
pip install requests pandas alpaca-py python-dotenv

Variables de entorno:
FMP_API_KEY=...
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...

DISCLAIMER: educativo, no asesoramiento financiero.
#pip install alpaca-py
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()
# -------------------------
# Config mínima
# -------------------------
SYMBOL = "AAPL"
DAYS = 120
FAST = 20
SLOW = 50
QTY = 1  # súper simple: comprar/vender 1 acción

FMP_API_KEY = os.getenv("FMP_API_KEY")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

FMP_BASE = "https://financialmodelingprep.com/api/v3"
os.environ.pop("SSLKEYLOGFILE", None)

def get_daily_close(symbol: str, days: int) -> pd.DataFrame:
    """
    Descarga histórico diario desde FMP y devuelve DataFrame ordenado con date y close.
    """
    url = f"{FMP_BASE}/historical-price-full/{symbol}"
    params = {"timeseries": days, "apikey": FMP_API_KEY}

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    hist = data.get("historical", [])
    if not hist:
        raise ValueError(f"No hay histórico para {symbol}. Respuesta: {data}")

    df = pd.DataFrame(hist)[["date", "close"]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def compute_signal(df: pd.DataFrame, fast: int, slow: int) -> int:
    """
    Señal simple:
    +1 = compra si SMA_fast cruza por encima de SMA_slow hoy
    -1 = venta si cruza por debajo hoy
     0 = nada
    """
    df = df.copy()
    df["sma_fast"] = df["close"].rolling(fast).mean()
    df["sma_slow"] = df["close"].rolling(slow).mean()

    df = df.dropna().reset_index(drop=True)
    if len(df) < 2:
        return 0

    prev = df.iloc[-2]
    last = df.iloc[-1]

    # Cruce alcista
    if prev["sma_fast"] <= prev["sma_slow"] and last["sma_fast"] > last["sma_slow"]:
        return 1

    # Cruce bajista
    if prev["sma_fast"] >= prev["sma_slow"] and last["sma_fast"] < last["sma_slow"]:
        return -1

    return 0


def get_position_qty(trading_client: TradingClient, symbol: str) -> int:
    """
    Devuelve cantidad de la posición actual. Si no existe, 0.
    """
    try:
        pos = trading_client.get_open_position(symbol)
        # pos.qty suele venir como string
        return int(float(pos.qty))
    except Exception:
        return 0


def place_market_order(trading_client: TradingClient, symbol: str, side: OrderSide, qty: int):
    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=side,
        time_in_force=TimeInForce.DAY
    )
    return trading_client.submit_order(order_data=order)


def main():
    if not FMP_API_KEY:
        raise RuntimeError("Falta FMP_API_KEY en variables de entorno.")
    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        raise RuntimeError("Faltan ALPACA_API_KEY y/o ALPACA_SECRET_KEY en variables de entorno.")

    # Alpaca paper = paper=True
    trading = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

    df = get_daily_close(SYMBOL, DAYS)
    signal = compute_signal(df, FAST, SLOW)

    pos_qty = get_position_qty(trading, SYMBOL)

    print(f"\nSymbol: {SYMBOL}")
    print(f"Último close: {df.iloc[-1]['close']:.2f}")
    print(f"Posición actual: {pos_qty} acciones")
    print(f"Señal: {signal} (1=BUY, -1=SELL, 0=HOLD)")

    if signal == 1 and pos_qty == 0:
        print(f"-> Enviando orden BUY {QTY} (paper)...")
        o = place_market_order(trading, SYMBOL, OrderSide.BUY, QTY)
        print(f"Orden enviada: id={o.id}")

    elif signal == -1 and pos_qty > 0:
        # cerramos todo (simple)
        print(f"-> Enviando orden SELL {pos_qty} (paper) para cerrar posición...")
        o = place_market_order(trading, SYMBOL, OrderSide.SELL, pos_qty)
        print(f"Orden enviada: id={o.id}")

    else:
        print("-> No se ejecuta ninguna orden hoy.")

    acct = trading.get_account()
    print("\n--- Cuenta (Alpaca Paper) ---")
    print(f"Equity: {acct.equity}")
    print(f"Cash: {acct.cash}")
    print(f"Buying power: {acct.buying_power}")


if __name__ == "__main__":
    main()
