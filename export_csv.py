import sqlite3
import csv


def export_to_csv():

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    cursor.execute("SELECT review_text, sentiment, score FROM reviews")

    rows = cursor.fetchall()

    with open("results.csv", "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow(["Review", "Sentiment", "Score"])

        writer.writerows(rows)

    conn.close()

    print("Results exported to results.csv")