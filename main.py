from db.db_connection import get_connection
from db.log_helpers import insert_headline,insert_nlp_analysis

from data.collector import fetch_price_data

from analysis.signal_generator import generate_signals
from analysis.risk_assessor import assess_risk
from analysis.nlp_insights import analyze_sentiment

from trades.trade_logger import log_signal

from data.news_fetcher import get_latest_headline

from config import SIGNAL_STRENGTH_THRESHOLD, BOT_VERSION, SYMBOL

import schedule
import time



def run_bot():
    symbol = SYMBOL
    df = fetch_price_data(symbol, period="7d", interval="1h")

    if not df.empty:
        signal = generate_signals(df)
        market_price = df.iloc[-1]['close']
        risk = assess_risk(df)
        headline = "Apple reports record quarterly revenue despite economic concerns."
        sentiment = analyze_sentiment(headline)
        sentiment_summary = f"{sentiment['sentiment'].capitalize()} ({sentiment['confidence']})"


        print("Risk Score:", risk)

        confidence = signal['confidence']
        risk_score = risk['risk_score']

        if confidence is not None and risk_score is not None:
            signal_strength = round(confidence * (1 - risk_score), 3)
        else:
            signal_strength = None

        # Log the strength score in the terminal
        print(f"Combined Signal Strength: {signal_strength}")

        # Apply suppression based on combined signal strength
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

        print("Signal Logged:", signal)

        print("DataFrame length after ta drop:", len(df))
        company_name = "Apple"
        headline = get_latest_headline(symbol, company_name)
        print("Latest headline:", headline)

        sentiment = analyze_sentiment(headline)
        sentiment_summary = f"{sentiment['sentiment'].capitalize()} ({sentiment['confidence']})"

        conn = get_connection()

        # 1. Store the headline
        headline_id = insert_headline(
            conn,
            symbol=symbol,
            text=headline,
            source="NewsAPI"
        )

        # 2. Store the sentiment
        nlp_id = insert_nlp_analysis(
            conn,
            sentiment=sentiment["sentiment"],
            confidence=sentiment["confidence"],
            model="FinBERT"
        )

        conn.close()


    else:
        print("No data to analyze.")

schedule.every(10).minutes.do(run_bot)

run_bot()  # optional: run immediately on container start

while True:
    schedule.run_pending()
    time.sleep(1)
