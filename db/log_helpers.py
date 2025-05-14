def insert_headline(conn, symbol, text, source="NewsAPI"):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO headlines (symbol, headline_text, source)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (symbol, text, source))
        return cursor.fetchone()[0]

def insert_nlp_analysis(conn, sentiment, confidence, model="FinBERT"):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO nlp_analysis (sentiment, confidence, model_used)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (sentiment, confidence, model))
        return cursor.fetchone()[0]
