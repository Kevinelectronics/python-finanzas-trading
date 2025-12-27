# -*- coding: utf-8 -*-
"""
insights_fmp_chatgpt.py

Genera insights financieros usando:
- Financial Modeling Prep (datos reales)
- ChatGPT (interpretación)

Flujo:
1) Precio (velas)
2) Fundamentales
3) Noticias
4) Contexto -> ChatGPT -> Insights

Educativo. No es asesoramiento financiero.
"""

import os
import requests
import pandas as pd
from openai import OpenAI
from datetime import datetime

os.environ.pop("SSLKEYLOGFILE", None)
# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------

# 🔐 OpenAI API Key (hardcodeada para simplificar la clase)
OPENAI_API_KEY = "your_api_key"

# 🔐 FMP API Key
FMP_API_KEY = "your_api_key"

SYMBOL = "AAPL"
BASE_URL = "https://financialmodelingprep.com/api/v3"


# ------------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------------

def safe_get(url: str, params: dict) -> dict:
    """GET robusto con timeout y errores claros."""
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


# ------------------------------------------------------------------
# FMP ENDPOINTS
# ------------------------------------------------------------------

def get_price_context(symbol: str) -> str:
    """Resumen simple de tendencia de precio."""
    url = f"{BASE_URL}/historical-price-full/{symbol}"
    params = {"timeseries": 60, "apikey": FMP_API_KEY}
    data = safe_get(url, params).get("historical", [])

    df = pd.DataFrame(data)[["date", "close"]]
    df["close"] = df["close"].astype(float)
    df = df.sort_values("date")

    trend = "uptrend" if df["close"].iloc[-1] > df["close"].iloc[0] else "downtrend"
    change_pct = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100

    return f"Price trend (last 60 days): {trend}, change: {change_pct:.2f}%"


def get_fundamentals_context(symbol: str) -> str:
    """Fundamentales clave."""
    url = f"{BASE_URL}/profile/{symbol}"
    params = {"apikey": FMP_API_KEY}
    p = safe_get(url, params)[0]

    return (
        f"Company: {p.get('companyName')}\n"
        f"Industry: {p.get('industry')}\n"
        f"Market Cap: {p.get('mktCap')}\n"
        f"P/E Ratio: {p.get('pe')}\n"
        f"Current Price: {p.get('price')}"
    )


def get_news_context(symbol: str) -> str:
    """Últimas noticias."""
    url = f"{BASE_URL}/stock_news"
    params = {"tickers": symbol, "limit": 3, "apikey": FMP_API_KEY}
    news = safe_get(url, params)

    if not news:
        return "Recent news: None"

    headlines = [f"- {n['title']}" for n in news]
    return "Recent news:\n" + "\n".join(headlines)


# ------------------------------------------------------------------
# CHATGPT
# ------------------------------------------------------------------

def generate_insights(context: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
You are a financial analyst.
You are NOT giving financial advice.

Based on the following context, provide:
1) Market summary (3 bullet points)
2) Key risks (3 bullet points)
3) Potential opportunities (3 bullet points)

Context:
{context}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content
def export_to_excel(symbol, price, fundamentals, news, insights):
    df = pd.DataFrame(
        [{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Symbol": symbol,
            "Price summary": price,
            "Fundamentals": fundamentals,
            "News": news,
            "ChatGPT insights": insights
        }]
    )

    filename = f"FFFfinancial_insights_{symbol}.xlsx"
    df.to_excel(filename, index=False)

    print(f"\n📊 Excel generado correctamente: {filename}")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

def main():
    price = get_price_context(SYMBOL)
    fundamentals = get_fundamentals_context(SYMBOL)
    news = get_news_context(SYMBOL)

    context = f"""
Asset: {SYMBOL}

{price}

Fundamentals:
{fundamentals}

{news}
""".strip()

    print("=== CONTEXT SENT TO CHATGPT ===")
    print(context)

    insights = generate_insights(context)

    print("\n=== CHATGPT INSIGHTS ===")
    print(insights)
    export_to_excel(SYMBOL, price, fundamentals, news, insights)


if __name__ == "__main__":
    main()
