import os
import schedule
import time
from datetime import datetime

from db.db_connection import get_connection
from db.log_helpers import insert_headline, insert_nlp_analysis

from data.collector import fetch_price_data
from analysis.signal_generator import generate_signals
from analysis.risk_assessor import assess_risk
from analysis.nlp_insights import analyze_sentiment

from trades.trade_logger import log_signal
from data.news_fetcher import get_latest_headline

from config import (
    SIGNAL_STRENGTH_THRESHOLD,
    BOT_VERSION
)


print(f"[BOOT] MCP container starting for SYMBOL={os.getenv('SYMBOL')}", flush=True)

def run_bot():

    print(f"[RUN] Running analysis for {os.getenv('SYMBOL')} at {datetime.now()}", flush=True)

    symbol = os.getenv("SYMBOL", "AAPL")
    print(f"[{datetime.now()}] Running analysis for {symbol}")
    
    df = fetch_price_data(symbol, period="7d", interval="1h")
    if df.empty:
        print(f"[{symbol}] No data to analyze.")
        return

    signal = generate_signals(df)
    market_price = df.iloc[-1]['close']
    risk = assess_risk(df)

    company_name = symbol
    headline = get_latest_headline(symbol, company_name)
    print(f"[{symbol}] Latest headline: {headline}")

    sentiment = analyze_sentiment(headline)
    sentiment_summary = f"{sentiment['sentiment'].capitalize()} ({sentiment['confidence']})"

    confidence = signal['confidence']
    risk_score = risk['risk_score']

    if confidence is not None and risk_score is not None:
        signal_strength = round(confidence * (1 - risk_score), 3)
    else:
        signal_strength = None

    print(f"[{symbol}] Risk Score: {risk}")
    print(f"[{symbol}] Combined Signal Strength: {signal_strength}")

    if signal_strength is None or signal_strength < SIGNAL_STRENGTH_THRESHOLD:
        signal['action'] = "HOLD"
        signal['reason'] = f"Signal strength {signal_strength} below threshold ({SIGNAL_STRENGTH_THRESHOLD})"

    log_signal(
        symbol=symbol,
        action=signal['action'],
        reason=signal['reason'],
        market_price=float(market_price),
        confidence=float(signal['confidence']) if signal['confidence'] is not None else None,
        risk=float(risk['risk_score']) if risk['risk_score'] is not None else None,
        sentiment=sentiment_summary,
        signal_strength=signal_strength,
        executed=False,
        source=BOT_VERSION
    )

    print(f"[{symbol}] Signal Logged: {signal}")

    conn = get_connection()
    insert_headline(conn, symbol=symbol, text=headline, source="NewsAPI")
    insert_nlp_analysis(conn, sentiment=sentiment["sentiment"], confidence=sentiment["confidence"], model="FinBERT")
    conn.close()


# Initial run
run_bot()

# Schedule every 15 minutes
schedule.every(15).minutes.do(run_bot)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
