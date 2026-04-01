import sqlite3

DB_NAME = "reviews.db"


# -----------------------------
# Create Database Connection
# -----------------------------
def create_connection():
    return sqlite3.connect(DB_NAME)


# -----------------------------
# Create Table
# -----------------------------
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_text TEXT,
            sentiment TEXT,
            score INTEGER
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Insert Single Result
# -----------------------------
def insert_result(result):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reviews (review_text, sentiment, score)
        VALUES (?, ?, ?)
    """, (
        result["review_text"],
        result["sentiment"],
        result["score"]
    ))

    conn.commit()
    conn.close()


# -----------------------------
# Bulk Insert (Milestone 2 Optimization)
# -----------------------------
def insert_bulk(results):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO reviews (review_text, sentiment, score)
        VALUES (?, ?, ?)
    """, [
        (r["review_text"], r["sentiment"], r["score"])
        for r in results
    ])

    conn.commit()
    conn.close()


# 
# Fetch All Results (for testing)
# 
def fetch_all():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reviews")
    rows = cursor.fetchall()

    conn.close()
    return rows