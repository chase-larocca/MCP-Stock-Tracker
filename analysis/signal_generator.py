import pandas as pd
import ta
import ta.momentum
import ta.trend

def generate_signals(df: pd.DataFrame) -> dict:
    """
    Generate basic trading signals from technical indicators.

    :param df: DataFrame from collector.py (must include OHLCV)
    :return: Dict with action ("BUY", "SELL", "HOLD"), reason, and confidence
    """
    if df.empty or 'close' not in df.columns:
        return {"action": "HOLD", "reason": "No valid price data", "confidence": None}

    try:
        df = df.copy()

        # Add technical indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['ema'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()

        # Remove rows with NaNs
        df.dropna(inplace=True)
        if df.empty:
            return {"action": "HOLD", "reason": "Insufficient data after computing indicators", "confidence": None}

        # Use most recent valid row
        latest = df.iloc[-1]

        # --- Confidence Calculation ---
        # Closer RSI is to 30 or 70, the stronger the signal (distance from 50 is a measure of strength)
        rsi_score = 1 - abs(latest['rsi'] - 50) / 50  # normalized between 0–1
        # MACD divergence from signal line
        macd_score = abs(latest['macd'] - latest['macd_signal']) / latest['close']
        # Price position above or below EMA
        ema_score = abs(latest['close'] - latest['ema']) / latest['close']

        # Final confidence: average of normalized indicators
        confidence = round(min((rsi_score + macd_score + ema_score) / 3, 1.0), 3)

        # Signal logic
        if latest['rsi'] < 30 and latest['macd'] > latest['macd_signal'] and latest['close'] > latest['ema']:
            return {
                "action": "BUY",
                "reason": "RSI < 30, MACD crossover, price above EMA",
                "confidence": confidence
            }
        elif latest['rsi'] > 70 and latest['macd'] < latest['macd_signal'] and latest['close'] < latest['ema']:
            return {
                "action": "SELL",
                "reason": "RSI > 70, MACD crossover down, price below EMA",
                "confidence": confidence
            }
        else:
            return {
                "action": "HOLD",
                "reason": "No strong signal (neutral indicators)",
                "confidence": confidence
            }

    except Exception as e:
        return {"action": "HOLD", "reason": f"Signal error: {str(e)}", "confidence": None}

