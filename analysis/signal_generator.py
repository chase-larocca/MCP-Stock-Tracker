import pandas as pd
import ta
import ta.momentum
import ta.trend
import json
import os
from datetime import datetime

def load_signal_config(symbol=None):
    """Load signal configuration - can be symbol-specific or default"""
    # Try symbol-specific first
    if symbol:
        symbol_config = f"strategies/symbol_specific/{symbol}_config.json"
        if os.path.exists(symbol_config):
            with open(symbol_config, 'r') as f:
                return json.load(f)
    
    # Fall back to default
    default_config = "strategies/default_config.json"
    if os.path.exists(default_config):
        with open(default_config, 'r') as f:
            return json.load(f)
    
    # Hardcoded fallback if no config files exist
    return {
        "weights": {
            "rsi": 0.4,
            "macd": 0.3,
            "ema_trend": 0.3
        },
        "thresholds": {
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "buy_threshold": 0.4,
            "sell_threshold": -0.4
        },
        "indicators": {
            "rsi_window": 14,
            "ema_short": 12,
            "ema_long": 26,
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9
        }
    }

def calculate_rsi(df, window=14):
    """Calculate RSI indicator"""
    return ta.momentum.RSIIndicator(df['close'], window=window).rsi()

def calculate_macd_histogram(df, fast=12, slow=26, signal=9):
    """Calculate MACD histogram"""
    macd = ta.trend.MACD(df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
    return macd.macd_diff()  # MACD histogram (MACD - Signal)

def calculate_ema_pair(df, short=12, long=26):
    """Calculate short and long EMA"""
    ema_short = ta.trend.EMAIndicator(df['close'], window=short).ema_indicator()
    ema_long = ta.trend.EMAIndicator(df['close'], window=long).ema_indicator()
    return ema_short, ema_long

def generate_signals(df: pd.DataFrame) -> dict:
    """
    Generate basic trading signals from technical indicators.
    Enhanced version with configurable strategy parameters.

    :param df: DataFrame from collector.py (must include OHLCV)
    :return: Dict with action ("BUY", "SELL", "HOLD"), reason, and confidence
    """
    if df.empty or 'close' not in df.columns:
        return {"action": "HOLD", "reason": "No valid price data", "confidence": None}

    try:
        # Load configuration (can be symbol-specific)
        # Note: We don't have symbol context in this function, but config system is ready
        config = load_signal_config()
        weights = config["weights"]
        thresholds = config["thresholds"]
        indicators = config["indicators"]
        
        df = df.copy()
        
        # Calculate indicators with configurable parameters
        df['rsi'] = calculate_rsi(df, indicators["rsi_window"])
        df['macd_hist'] = calculate_macd_histogram(df, indicators["macd_fast"], 
                                                   indicators["macd_slow"], indicators["macd_signal"])
        df['ema_short'], df['ema_long'] = calculate_ema_pair(df, indicators["ema_short"], 
                                                            indicators["ema_long"])

        # Remove rows with NaNs
        df.dropna(inplace=True)
        if df.empty:
            return {"action": "HOLD", "reason": "Insufficient data after computing indicators", "confidence": None}

        # Use most recent valid row
        latest = df.iloc[-1]
        latest_close = latest['close']
        latest_rsi = latest['rsi']
        latest_macd = latest['macd_hist']
        latest_ema_short = latest['ema_short']
        latest_ema_long = latest['ema_long']

        # Initialize scoring
        confidence_score = 0
        reasons = []
        
        # RSI contribution
        if latest_rsi < thresholds["rsi_oversold"]:
            confidence_score += weights['rsi']
            reasons.append(f"RSI oversold ({latest_rsi:.1f})")
        elif latest_rsi > thresholds["rsi_overbought"]:
            confidence_score -= weights['rsi']
            reasons.append(f"RSI overbought ({latest_rsi:.1f})")
        else:
            reasons.append(f"RSI neutral ({latest_rsi:.1f})")
        
        # MACD contribution
        if latest_macd > 0:
            confidence_score += weights['macd']
            reasons.append("MACD histogram positive")
        elif latest_macd < 0:
            confidence_score -= weights['macd']
            reasons.append("MACD histogram negative")
        else:
            reasons.append("MACD histogram neutral")
        
        # EMA trend contribution
        if latest_ema_short > latest_ema_long:
            confidence_score += weights['ema_trend']
            reasons.append("EMA uptrend")
        elif latest_ema_short < latest_ema_long:
            confidence_score -= weights['ema_trend']
            reasons.append("EMA downtrend")
        else:
            reasons.append("EMA sideways")

        # Normalize final confidence
        max_possible = sum(weights.values())
        normalized_confidence = confidence_score / max_possible  # Range: -1 to 1
        
        # Calculate absolute confidence for return value
        confidence = round(abs(normalized_confidence), 3)
        
        # Map to action using configurable thresholds
        if normalized_confidence >= thresholds["buy_threshold"]:
            return {
                "action": "BUY",
                "reason": " | ".join(reasons) + f" (score: {normalized_confidence:.2f})",
                "confidence": confidence
            }
        elif normalized_confidence <= thresholds["sell_threshold"]:
            return {
                "action": "SELL",
                "reason": " | ".join(reasons) + f" (score: {normalized_confidence:.2f})",
                "confidence": confidence
            }
        else:
            return {
                "action": "HOLD",
                "reason": " | ".join(reasons) + f" (score: {normalized_confidence:.2f})",
                "confidence": confidence
            }

    except Exception as e:
        return {"action": "HOLD", "reason": f"Signal error: {str(e)}", "confidence": None}

# Additional function for enhanced analysis (optional - for future LLM integration)
def generate_signals_detailed(df: pd.DataFrame, symbol: str = None) -> dict:
    """
    Enhanced version that includes detailed breakdown for LLM analysis.
    This is the function that will be used by the LLM strategist.
    
    :param df: DataFrame from collector.py
    :param symbol: Symbol for symbol-specific configs
    :return: Detailed signal analysis
    """
    if df.empty or 'close' not in df.columns:
        return {"action": "HOLD", "reason": "No valid price data", "confidence": None, "details": {}}

    try:
        config = load_signal_config(symbol)
        weights = config["weights"]
        thresholds = config["thresholds"]
        indicators = config["indicators"]
        
        df = df.copy()
        
        # Calculate indicators
        df['rsi'] = calculate_rsi(df, indicators["rsi_window"])
        df['macd_hist'] = calculate_macd_histogram(df, indicators["macd_fast"], 
                                                   indicators["macd_slow"], indicators["macd_signal"])
        df['ema_short'], df['ema_long'] = calculate_ema_pair(df, indicators["ema_short"], 
                                                            indicators["ema_long"])

        df.dropna(inplace=True)
        if df.empty:
            return {"action": "HOLD", "reason": "Insufficient data", "confidence": None, "details": {}}

        latest = df.iloc[-1]
        
        # Detailed component analysis
        components = {}
        confidence_score = 0
        reasons = []
        
        # RSI analysis
        rsi_val = latest['rsi']
        if rsi_val < thresholds["rsi_oversold"]:
            rsi_contrib = weights['rsi']
            rsi_signal = "BUY"
            rsi_reason = f"RSI oversold ({rsi_val:.1f})"
        elif rsi_val > thresholds["rsi_overbought"]:
            rsi_contrib = -weights['rsi']
            rsi_signal = "SELL"
            rsi_reason = f"RSI overbought ({rsi_val:.1f})"
        else:
            rsi_contrib = 0
            rsi_signal = "NEUTRAL"
            rsi_reason = f"RSI neutral ({rsi_val:.1f})"
        
        components['rsi'] = {
            'value': rsi_val,
            'contribution': rsi_contrib,
            'signal': rsi_signal,
            'reason': rsi_reason,
            'weight': weights['rsi']
        }
        confidence_score += rsi_contrib
        reasons.append(rsi_reason)
        
        # MACD analysis
        macd_val = latest['macd_hist']
        if macd_val > 0:
            macd_contrib = weights['macd']
            macd_signal = "BUY"
            macd_reason = "MACD histogram positive"
        elif macd_val < 0:
            macd_contrib = -weights['macd']
            macd_signal = "SELL"
            macd_reason = "MACD histogram negative"
        else:
            macd_contrib = 0
            macd_signal = "NEUTRAL"
            macd_reason = "MACD histogram neutral"
        
        components['macd'] = {
            'value': macd_val,
            'contribution': macd_contrib,
            'signal': macd_signal,
            'reason': macd_reason,
            'weight': weights['macd']
        }
        confidence_score += macd_contrib
        reasons.append(macd_reason)
        
        # EMA analysis
        ema_short_val = latest['ema_short']
        ema_long_val = latest['ema_long']
        if ema_short_val > ema_long_val:
            ema_contrib = weights['ema_trend']
            ema_signal = "BUY"
            ema_reason = "EMA uptrend"
        elif ema_short_val < ema_long_val:
            ema_contrib = -weights['ema_trend']
            ema_signal = "SELL"
            ema_reason = "EMA downtrend"
        else:
            ema_contrib = 0
            ema_signal = "NEUTRAL"
            ema_reason = "EMA sideways"
        
        components['ema_trend'] = {
            'short_ema': ema_short_val,
            'long_ema': ema_long_val,
            'contribution': ema_contrib,
            'signal': ema_signal,
            'reason': ema_reason,
            'weight': weights['ema_trend']
        }
        confidence_score += ema_contrib
        reasons.append(ema_reason)
        
        # Final calculation
        max_possible = sum(weights.values())
        normalized_confidence = confidence_score / max_possible
        confidence = round(abs(normalized_confidence), 3)
        
        # Determine action
        if normalized_confidence >= thresholds["buy_threshold"]:
            action = "BUY"
        elif normalized_confidence <= thresholds["sell_threshold"]:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            "action": action,
            "reason": " | ".join(reasons) + f" (score: {normalized_confidence:.2f})",
            "confidence": confidence,
            "details": {
                "raw_score": confidence_score,
                "normalized_score": normalized_confidence,
                "components": components,
                "config_used": config,
                "price": latest['close'],
                "strongest_signal": max(components.items(), key=lambda x: abs(x[1]['contribution']))[0],
                "conflicting_signals": len([c for c in components.values() if 
                                          (c['signal'] == 'BUY' and action == 'SELL') or 
                                          (c['signal'] == 'SELL' and action == 'BUY')])
            }
        }

    except Exception as e:
        return {"action": "HOLD", "reason": f"Signal error: {str(e)}", "confidence": None, "details": {}}