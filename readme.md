Parallel Text Processing Dashboard
 Overview

The Parallel Text Processing Dashboard is a Streamlit-based web application designed to efficiently process and analyze large text datasets. It performs sentiment analysis using a rule-based approach and provides an interactive UI for uploading files, viewing results, searching keywords, and downloading reports.

🎯 Features
📂 Upload multiple files (TXT, CSV, Excel)
⚙️ Process large datasets efficiently
😊 Sentiment Analysis (Positive / Negative / Neutral)
📊 Interactive Dashboard (metrics & charts)
🔍 Keyword Search functionality
📥 Download results as CSV
🧹 Clear uploaded data option
⏱️ Processing time tracking
📈 Performance metrics (speed, counts)
🖥️ User-friendly and colorful UI
🧠 How It Works
User uploads text/CSV/Excel file(s)
System extracts textual data automatically
Each line is processed individually
Sentiment score is calculated using rule-based logic
Results are displayed in dashboard and charts
📊 Sentiment Analysis Logic
Positive words → add score
Negative words → subtract score
Final score determines sentiment:
Score	Sentiment
> 0	Positive
< 0	Negative
= 0	Neutral
⚡ Processing Types
Sequential Processing (current implementation)
Parallel Processing (can be extended using multiprocessing)
🧪 Edge Cases Handled
❌ Empty input → shows “No data to process”
⚠️ Invalid data → skipped safely
🔁 Repeated words → counted multiple times
📦 Large files → handled efficiently
🛠️ Tech Stack
Python 🐍
Streamlit 🌐
Pandas 📊
Matplotlib 📈
📂 Supported File Formats
.txt
.csv
.xlsx

📈 Performance Metrics
Processing Time
Execution Speed (rows/sec)
Sentiment Distribution
Accuracy (estimated)

 Future Enhancements
 AI-based sentiment analysis (NLP models)
 Multi-language support
 Advanced analytics dashboard
