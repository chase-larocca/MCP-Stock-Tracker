import pandas as pd
import ta.volatility

import pandas as pd
import ta.volatility

def assess_risk(df: pd.DataFrame) -> dict:
    """
    Assess risk level of an asset based on volatility and drawdown.

    :param df: Price history DataFrame from collector.py
    :return: Dictionary with risk score and explanation
    """
    if df.empty or 'close' not in df.columns:
        return {"risk_score": None, "reason": "No valid data"}

    try:
        df = df.copy()
        df['close'] = pd.to_numeric(df['close'])

        # Calculate ATR (Average True Range)
        atr = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=14
        )
        df['atr'] = atr.average_true_range()

        # Volatility score: normalize ATR vs. current price
        latest_atr = df['atr'].iloc[-1]
        latest_price = df['close'].iloc[-1]
        volatility_score = latest_atr / latest_price if latest_price > 0 else 0

        # Calculate drawdown
        df['rolling_max'] = df['close'].rolling(window=20).max()
        df['drawdown'] = (df['rolling_max'] - df['close']) / df['rolling_max']
        latest_drawdown = df['drawdown'].iloc[-1]

        # Combine into risk score
        raw_risk = volatility_score + latest_drawdown
        normalized_risk = min(round(raw_risk, 2), 1.0)  # cap at 1.0

        return {
            "risk_score": normalized_risk,
            "reason": f"ATR: {round(volatility_score, 3)}, Drawdown: {round(latest_drawdown, 3)}"
        }

    except Exception as e:
        return {"risk_score": None, "reason": f"Risk assessment error: {str(e)}"}
