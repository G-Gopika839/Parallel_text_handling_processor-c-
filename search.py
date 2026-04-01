import sqlite3

def search_by_sentiment(sentiment):

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT review_text, score FROM reviews WHERE sentiment=?",
        (sentiment,)
    )

    rows = cursor.fetchall()

    for r in rows:
        print(r)

    conn.close()
    