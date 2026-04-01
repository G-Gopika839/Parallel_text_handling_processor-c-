import sqlite3
from datetime import datetime


# create database and table
def create_table():

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    # Main storage table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_text TEXT,
        sentiment TEXT,
        score INTEGER,
        filename TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- MIGRATION: Add columns if they don't exist ---
    cursor.execute("PRAGMA table_info(reviews)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "filename" not in columns:
        cursor.execute("ALTER TABLE reviews ADD COLUMN filename TEXT DEFAULT 'Legacy'")
    if "processed_at" not in columns:
        cursor.execute("ALTER TABLE reviews ADD COLUMN processed_at TIMESTAMP")
        cursor.execute("UPDATE reviews SET processed_at = CURRENT_TIMESTAMP WHERE processed_at IS NULL")

    # FTS5 Virtual Table for lightning-fast search
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS reviews_fts 
    USING fts5(review_text, content='reviews', content_rowid='id')
    """)

    conn.commit()
    conn.close()


# create index for faster query
def create_index():

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_sentiment
    ON reviews(sentiment)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_processed_at
    ON reviews(processed_at)
    """)

    conn.commit()
    conn.close()

    print("Database indexes created for faster queries")


# insert multiple records
def insert_reviews(results, filename="Manual Input"):

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data for main table
    # Expected result format: (review_text, sentiment, score)
    data_to_insert = []
    for r in results:
        data_to_insert.append((r[0], r[1], r[2], filename, now))

    cursor.executemany(
        "INSERT INTO reviews (review_text, sentiment, score, filename, processed_at) VALUES (?, ?, ?, ?, ?)",
        data_to_insert
    )
    
    # Update FTS index
    cursor.execute("INSERT INTO reviews_fts(reviews_fts) VALUES('rebuild')")

    conn.commit()
    conn.close()


# view all records
def fetch_all(limit=1000):

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reviews ORDER BY processed_at DESC LIMIT ?", (limit,))

    rows = cursor.fetchall()

    conn.close()

    return rows


# Full-Text Search
def search_reviews_fts(query):
    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT r.review_text, r.sentiment, r.score, r.filename, r.processed_at
    FROM reviews r
    JOIN reviews_fts f ON r.id = f.rowid
    WHERE reviews_fts MATCH ?
    ORDER BY rank
    """, (query,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows


# sentiment distribution query
def sentiment_distribution():

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT sentiment, COUNT(*) 
    FROM reviews
    GROUP BY sentiment
    """)

    rows = cursor.fetchall()

    conn.close()

    print("\nSentiment Distribution (From Database)")
    print("--------------------------------------")

    for sentiment, count in rows:
        print(sentiment, ":", count)