import time
import itertools
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

from loader import load_file
from rule_engine import analyze_text
from database import create_table, create_index, insert_reviews


# Sequential Processing
def sequential_processing(reviews):

    results = []

    for review in reviews:
        res = analyze_text(review)
        results.append((review, res["sentiment"], res["score"]))

    return results


# Thread Processing
def thread_processing(reviews):

    results = []

    with ThreadPoolExecutor(max_workers=8) as executor:

        output = executor.map(analyze_text, reviews)

        for review, res in zip(reviews, output):
            results.append((review, res["sentiment"], res["score"]))

    return results


# Multiprocessing
def process_review(review):
    res = analyze_text(review)
    return (res["sentiment"], res["score"])

def process_review_chunk(chunk):
    return [process_review(review) for review in chunk]

def multiprocessing_processing(reviews):
    start = time.perf_counter()

    import os
    cores = os.cpu_count() or 4
    chunk_size = max(500, len(reviews) // (cores * 4))
    chunks = [reviews[i:i + chunk_size] for i in range(0, len(reviews), chunk_size)]
    with Pool() as pool:
        chunked_results = pool.map(process_review_chunk, chunks)
    
    results_only = list(itertools.chain.from_iterable(chunked_results))
    results = []
    for review, res_data in zip(reviews, results_only):
        results.append((review, res_data[0], res_data[1]))
    end = time.perf_counter()
    


    return results


# Insert into database and measure time
def insert_into_db(results):

    start = time.perf_counter()

    insert_reviews(results)

    end = time.perf_counter()

    return end - start


# Query time measurement
def query_time():

    conn = sqlite3.connect("results.db")
    cursor = conn.cursor()

    start = time.perf_counter()

    cursor.execute("SELECT * FROM reviews WHERE sentiment='Positive'")
    cursor.fetchall()

    end = time.perf_counter()

    conn.close()

    return end - start


# Sentiment distribution
def sentiment_distribution(results):

    positive = 0
    negative = 0
    neutral = 0

    for r in results:

        sentiment = r[1]

        if sentiment == "Positive":
            positive += 1
        elif sentiment == "Negative":
            negative += 1
        else:
            neutral += 1

    total = positive + negative + neutral

    print("\nSentiment Distribution")
    print("----------------------")
    print("Positive:", positive)
    print("Negative:", negative)
    print("Neutral :", neutral)


# Run performance test
def run_test(size):

    print("\nTesting with", size, "reviews")

    reviews = load_file("bigdata.txt")
    if len(reviews) < size:
        reviews = reviews * (size // len(reviews) + 1)
    reviews = reviews[:size]

    create_table()
    create_index()

    # Sequential
    start = time.perf_counter()
    results = sequential_processing(reviews)
    end = time.perf_counter()

    print("Sequential processing:", round(end - start,6))

    insert_time = insert_into_db(results)
    print("Insert time:", insert_time)

    q_time = query_time()
    print("Query time:", q_time)

    sentiment_distribution(results)

    # Threading
    start = time.perf_counter()
    thread_processing(reviews)
    end = time.perf_counter()

    print("Threading time:", end - start)

    # Multiprocessing
    start = time.perf_counter()
    multiprocessing_processing(reviews)
    end = time.perf_counter()

    print("Multiprocessing time:", end - start)


# Main execution
if __name__ == "__main__":

    run_test(100)
    run_test(100000)
    run_test(1000000)