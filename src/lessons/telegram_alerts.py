# -*- coding: utf-8 -*-
"""
pipeline_insights_telegram.py

Pipeline completo (Clase 3):
- FMP: velas + fundamentales + noticias
- ChatGPT: genera insights
- Excel: exporta resultados
- Telegram: envía alerta con resumen

Educativo. No es asesoramiento financiero.
"""

from datetime import datetime
import requests
import pandas as pd
from openai import OpenAI
import os
os.environ.pop("SSLKEYLOGFILE", None)

# ------------------------------------------------------------
# CONFIG (hardcodeado para simplificar Udemy)
# ------------------------------------------------------------

SYMBOL = "AAPL"

# FMP
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# OpenAI
# 🔐 OpenAI API Key (hardcodeada para simplificar la clase)
OPENAI_API_KEY = "you_api_key"
OPENAI_MODEL = "gpt-4o-mini"
# 🔐 FMP API Key
FMP_API_KEY = "your_api_key"

# Telegram
TELEGRAM_BOT_TOKEN = "you_telegram_token"
TELEGRAM_CHAT_ID = "438535917"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def safe_get(url: str, params: dict):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def safe_post(url: str, data: dict):
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    return r.json()


# ------------------------------------------------------------
# FMP Data
# ------------------------------------------------------------

def get_price_summary(symbol: str, days: int = 60) -> str:
    url = f"{FMP_BASE_URL}/historical-price-full/{symbol}"
    params = {"timeseries": days, "apikey": FMP_API_KEY}
    j = safe_get(url, params)

    hist = j.get("historical", [])
    if not hist:
        raise RuntimeError(f"FMP no devolvió histórico para {symbol}. Respuesta: {j}")

    df = pd.DataFrame(hist)[["date", "close"]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["close"] = df["close"].astype(float)
    df = df.sort_values("date").reset_index(drop=True)

    start = df["close"].iloc[0]
    end = df["close"].iloc[-1]
    change_pct = (end / start - 1) * 100
    trend = "uptrend" if end > start else "downtrend"

    return f"Price trend ({days}d): {trend}, change: {change_pct:.2f}% (from {start:.2f} to {end:.2f})"

def get_fundamentals(symbol: str) -> str:
    url = f"{FMP_BASE_URL}/profile/{symbol}"
    params = {"apikey": FMP_API_KEY}
    j = safe_get(url, params)

    if not isinstance(j, list) or not j:
        raise RuntimeError(f"FMP profile vacío para {symbol}. Respuesta: {j}")

    p = j[0]
    return (
        f"Company: {p.get('companyName')}\n"
        f"Industry: {p.get('industry')}\n"
        f"Market Cap: {p.get('mktCap')}\n"
        f"P/E Ratio: {p.get('pe')}\n"
        f"Current Price: {p.get('price')}"
    )

def get_news(symbol: str, limit: int = 3) -> str:
    url = f"{FMP_BASE_URL}/stock_news"
    params = {"tickers": symbol, "limit": limit, "apikey": FMP_API_KEY}
    j = safe_get(url, params)

    if not isinstance(j, list) or not j:
        return "Recent news:\n- None returned"

    lines = []
    for n in j[:limit]:
        title = n.get("title", "No title")
        site = n.get("site", "")
        # date viene a veces como publishedDate o date; lo manejamos suave
        dt = n.get("publishedDate") or n.get("date") or ""
        lines.append(f"- {title} ({site}) {dt}".strip())

    return "Recent news:\n" + "\n".join(lines)


# ------------------------------------------------------------
# ChatGPT Insights
# ------------------------------------------------------------

def generate_insights(symbol: str, context: str) -> str:
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
You are a finance analyst.
You are NOT giving financial advice.

Asset: {symbol}

Based on the context, write:
1) Market summary (3 bullets)
2) Key risks (3 bullets)
3) Potential opportunities (3 bullets)

Keep it clear and actionable. Avoid hype.

Context:
{context}
""".strip()

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content


# ------------------------------------------------------------
# Excel Export
# ------------------------------------------------------------

def export_to_excel(symbol: str, price: str, fundamentals: str, news: str, insights: str) -> str:
    df = pd.DataFrame([{
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "price_summary": price,
        "fundamentals": fundamentals,
        "news": news,
        "chatgpt_insights": insights
    }])

    filename = f"financial_insights_{symbol}.xlsx"
    df.to_excel(filename, index=False)
    return filename


# ------------------------------------------------------------
# Telegram
# ------------------------------------------------------------

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        # Markdown simple (sin cosas raras)
        "parse_mode": "Markdown"
    }
    safe_post(url, payload)


def build_telegram_message(symbol: str, price: str, insights: str, excel_filename: str) -> str:
    # Ojo: Telegram Markdown a veces se rompe con caracteres raros.
    # Por eso mantenemos el formato simple.
    msg = (
        f"📊 *Financial Insights2*\n"
        f"*Asset:* {symbol}\n\n"
        f"*Price:* {price}\n\n"
        f"*Insights:*\n{insights}\n\n"
        f"✅ Excel generado: {excel_filename}"
    )
    return msg


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    # 1) Datos FMP
    price = get_price_summary(SYMBOL, days=60)
    fundamentals = get_fundamentals(SYMBOL)
    news = get_news(SYMBOL, limit=3)

    # 2) Contexto para ChatGPT
    context = f"""
{price}

Fundamentals:
{fundamentals}

{news}
""".strip()

    print("=== CONTEXT SENT TO CHATGPT ===")
    print(context)

    # 3) Insights
    insights = generate_insights(SYMBOL, context)

    print("\n=== CHATGPT INSIGHTS ===")
    print(insights)

    # 4) Export Excel
    excel_file = export_to_excel(SYMBOL, price, fundamentals, news, insights)
    print(f"\nExcel generado: {excel_file}")

    # 5) Telegram
    telegram_text = build_telegram_message(SYMBOL, price, insights, excel_file)
    send_telegram_message(telegram_text)
    print("\nMensaje enviado a Telegram ✅")


if __name__ == "__main__":
    main()
