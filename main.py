import os
import time
import itertools
from loader import load_file
from rule_engine import analyze_text
from database import create_table,insert_reviews
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

from search import search_by_sentiment

search_by_sentiment("Negative")
from export_csv import export_to_csv

export_to_csv()

def process_review(review):
    return analyze_text(review)

def process_review_chunk(chunk):
    return [analyze_text(review) for review in chunk]


if __name__ == "__main__":

    # 1️⃣ Load Reviews
    reviews = load_file("bigdata.txt")

    # 2️⃣ Ensure Minimum 100 Reviews
   # if len(reviews) < 100:
       # reviews = reviews * (100 // len(reviews) + 1)

    #reviews = reviews[:100] 
        #reviews = reviews * (10000 // len(reviews) + 1)
        #test_reviews = test_reviews[:10000]# exactly 100
        #test_reviews = reviews * (100000 // len(reviews) + 1)
        #test_reviews = test_reviews[:100000]

    create_table()

    # 
    # SINGLE PROCESSING
    # 
    start = time.perf_counter()

    single_results = []
    for review in reviews:
        single_results.append(process_review(review))

    single_time = time.perf_counter() - start
    print("Single Processing Time:", single_time)

    # Store results (only once to DB)
    insert_reviews(single_results)

    # 
    #  THREADING
    # 
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=4) as executor:
        thread_results = list(executor.map(process_review, reviews))

    thread_time = time.perf_counter() - start
    print("Threading Time:", thread_time)

    
    #  MULTIPROCESSING
     
    start = time.perf_counter()

    cores = os.cpu_count() or 4
    chunk_size = max(500, len(reviews) // (cores * 4))
    chunks = [reviews[i:i + chunk_size] for i in range(0, len(reviews), chunk_size)]
    with Pool() as pool:
        chunked_results = pool.map(process_review_chunk, chunks)
    
    mp_results = list(itertools.chain.from_iterable(chunked_results))

    mp_time = time.perf_counter() - start
    print("Multiprocessing Time:", mp_time)