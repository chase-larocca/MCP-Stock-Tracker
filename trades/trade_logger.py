import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# Function to insert the properties of a trade into the SQL database 
def log_trade(symbol, action, reason, confidence, risk, sentiment):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (
              symbol
            , action
            , signal_reason
            , confidence_score
            , risk_score
            , sentiment_summary
            )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (symbol, action, reason, confidence, risk, sentiment))
    conn.commit()
    cursor.close()
    conn.close()

# Log signal data in the trades table
def log_signal(
    symbol,
    action,
    reason,
    market_price,
    confidence=None,
    risk=None,
    sentiment=None,
    signal_strength=None,
    executed=False,
    source="MCP-BOT",
    headline_id=None,
    nlp_id=None
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (
            symbol
        , action
        , signal_reason
        , confidence_score
        , risk_score
        , market_price
        , signal_strength
        , is_executed
        , signal_only
        , source
        , headline_id
        , nlp_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        str(symbol),
        str(action),
        str(reason),
        float(confidence) if confidence is not None else None,
        float(risk) if risk is not None else None,
        float(market_price),
        float(signal_strength) if signal_strength is not None else None,
        bool(executed),
        bool(not executed),
        str(source),
        int(headline_id) if headline_id is not None else None,
        int(nlp_id) if nlp_id is not None else None
    ))

    conn.commit()
    cursor.close()
    conn.close()

# Function to receive the most recent trade executed by the system 
def get_latest_trade():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 1")
    trade = cursor.fetchone()
    cursor.close()
    conn.close()
    return trade