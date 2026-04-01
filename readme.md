# Python Parallel Text Handling Processor

## Overview
This project implements a weighted rule-based sentiment analysis system for processing large text datasets. It classifies reviews as Positive, Negative, or Neutral and stores results in an SQLite database. It also compares execution performance using single processing, multithreading, and multiprocessing.

## Features
- Weighted sentiment scoring
- Minimum 100 reviews processed
- SQLite database storage
- Performance comparison:
  - Single for-loop
  - ThreadPoolExecutor
  - Multiprocessing Pool

## Sentiment Logic
Each keyword has a weight.
Score > 0 → Positive  
Score < 0 → Negative  
Score = 0 → Neutral  

## Database Structure
Database: reviews.db  
Table: reviews  

Columns:
- id (INTEGER PRIMARY KEY)
- review_text (TEXT)
- sentiment (TEXT)
- score (INTEGER)


## Concepts Used
- File handling
- Rule-based text processing
- SQLite integration
- Multithreading
- Multiprocessing
- Performance benchmarking

