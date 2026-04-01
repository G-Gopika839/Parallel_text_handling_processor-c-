import streamlit as st
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import os
import concurrent.futures
import itertools
from rule_engine import analyze_text
from database import create_table, create_index, insert_reviews, fetch_all, search_reviews_fts

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Text Processing System", layout="wide")

st.title(" Parallel Text Processing Dashboard")

# Initialize Database
create_table()
create_index()
st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027, #203a43, #2c5364);
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #ff7e5f, #feb47b);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px;
    font-weight: bold;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 15px;
}

/* Text input */
.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.1);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION BUTTONS ----------------
col1, col2, col3, col4 = st.columns(4)

if col1.button("📊 Dashboard", use_container_width=True):
    st.session_state["nav"] = "dashboard"

if col2.button("🔍 Search", use_container_width=True):
    st.session_state["nav"] = "search"

if col3.button("📤 Export", use_container_width=True):
    st.session_state["nav"] = "export"

if col4.button("✍️ Manual Input", use_container_width=True):
    st.session_state["nav"] = "manual"

if st.button("📜 View History", use_container_width=True):
    st.session_state["nav"] = "history"

if "nav" not in st.session_state:
    st.session_state["nav"] = "dashboard"

# ---------------- CACHED PROCESSING ----------------
def process_chunk_parallel(chunk):
    res_list = []
    for r in chunk:
        if r.strip() != "":
            res = analyze_text(r)
            res_list.append((res["score"], res["sentiment"], res["pos_count"], res["neg_count"]))
    return res_list

@st.cache_resource
def get_executor():
    return concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count() or 4)

@st.cache_data
def run_processing_pipeline(reviews):
    """
    Runs both normal loop (for comparison) and parallel processing, returning results.
    Caching ensures identical uploads won't be redundantly processed.
    """
    # 1. Normal Processing
    start_time_normal = time.time()
    for review in reviews:
        if review.strip() != "":
            _ = analyze_text(review)  # Just compute to measure exact time
    normal_time = time.time() - start_time_normal

    # 2. Parallel Processing
    start_time_parallel = time.time()
    results_parallel = []

    cores = os.cpu_count() or 4
    chunk_size = max(500, len(reviews) // (cores * 4))
    chunks = [reviews[i:i + chunk_size] for i in range(0, len(reviews), chunk_size)]
    
    executor = get_executor()
    chunk_results = list(executor.map(process_chunk_parallel, chunks))
    results_parallel = list(itertools.chain.from_iterable(chunk_results))

    parallel_time = time.time() - start_time_parallel

    df = pd.DataFrame(
        results_parallel,
        columns=["Sentiment Score", "Sentiment", "Pos Words", "Neg Words"]
    )
    df.insert(0, "Text", reviews)
    
    return normal_time, parallel_time, df

# ---------------- SIDEBAR ----------------
st.sidebar.header("Upload and Processing")

uploaded_files = st.sidebar.file_uploader(
    "Upload TXT / CSV / Excel Files",
    type=["txt", "csv", "xlsx"],
    accept_multiple_files=True
)

st.sidebar.write(f"📂 Number of Files Uploaded: {len(uploaded_files) if uploaded_files else 0}")


start_button = st.sidebar.button("Start Processing")

# ---------------- FILE HANDLING (MULTIPLE FILES + FULL DOCUMENT) ----------------
@st.cache_data
def process_uploaded_files(uploaded_files):
    all_reviews = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type

        if file_type == "text/plain":
            text = uploaded_file.getvalue().decode("utf-8")
            reviews = text.split("\n")
            reviews = [r for r in reviews if r.strip() != ""]
            all_reviews.extend(reviews)

        elif file_type == "text/csv" or uploaded_file.name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, engine="python", on_bad_lines="skip")
                if not df.empty and len(df.columns) > 0:
                    text_column = None
                    for col in df.columns:
                        if df[col].dtype == "object":
                            text_column = col
                            break
                    if text_column is None:
                        text_column = df.columns[0]
                    reviews = df[text_column].dropna().astype(str).tolist()
                    all_reviews.extend(reviews)
            except Exception:
                pass

        elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or uploaded_file.name.endswith((".xls", ".xlsx")):
            try:
                df = pd.read_excel(uploaded_file)
                if not df.empty and len(df.columns) > 0:
                    text_column = None
                    for col in df.columns:
                        if df[col].dtype == "object":
                            text_column = col
                            break
                    if text_column is None:
                        text_column = df.columns[0]
                    reviews = df[text_column].dropna().astype(str).tolist()
                    all_reviews.extend(reviews)
            except Exception:
                pass
    return all_reviews

if uploaded_files is not None and len(uploaded_files) > 0:
    all_reviews = process_uploaded_files(uploaded_files)

    if len(all_reviews) == 0:
        st.warning("no data to process, upload valid file")
        if "reviews" in st.session_state:
            del st.session_state["reviews"]
    else:
        st.session_state["reviews"] = all_reviews
        st.success(f"Loaded {len(all_reviews)} lines for processing across all files")
        
        

# ---------------- PROCESSING ----------------
if start_button and "reviews" in st.session_state:
    reviews = st.session_state["reviews"]
    start_timestamp = datetime.now()

    with st.spinner("Processing... ⏳"):
        normal_time, parallel_time, results_df = run_processing_pipeline(reviews)
        end_timestamp = datetime.now()

        st.session_state["results_df"] = results_df
        st.session_state["normal_time"] = normal_time
        st.session_state["parallel_time"] = parallel_time
        st.session_state["processing_time"] = parallel_time
        st.session_state["start_time"] = start_timestamp
        st.session_state["end_time"] = end_timestamp

        # --- PERSIST TO DATABASE ---
        # Combine text with results for insertion
        # results_df columns are ["Text", "Sentiment Score", "Sentiment", "Pos Words", "Neg Words"]
        db_ready_results = []
        for _, row in results_df.iterrows():
            db_ready_results.append((row["Text"], row["Sentiment"], int(row["Sentiment Score"])))
        
        # Get filename(s)
        filenames = ", ".join([f.name for f in uploaded_files]) if uploaded_files else "Manual Input"
        insert_reviews(db_ready_results, filenames)

    st.success("✅ Processing Completed")

if st.button("🗑️ Reset / Clear Data"):
    st.session_state.clear()
    st.cache_data.clear()
    st.success("✅ Data cleared successfully")
    st.rerun()   # 🔥 IMPORTANT (forces UI refresh)

# ---------------- DASHBOARD ----------------
if st.session_state["nav"] == "dashboard":

    st.subheader("📊 Dashboard")

    if "results_df" in st.session_state:
        results_df = st.session_state["results_df"]

        total = len(results_df)
        strong_positive = (results_df["Sentiment"] == "Strong Positive").sum()
        positive = (results_df["Sentiment"] == "Positive").sum()
        negative = (results_df["Sentiment"] == "Negative").sum()
        strong_negative = (results_df["Sentiment"] == "Strong Negative").sum()
        neutral = (results_df["Sentiment"] == "Neutral").sum()

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("📄 Lines", total)
        col2.metric("⚡ Strong Pos", strong_positive)
        col3.metric(" Positive", positive)
        col4.metric(" Negative", negative)
        col5.metric("🚨 Strong Neg", strong_negative)
        col6.metric(" Neutral", neutral)

        # ---------------- Comparison Metrics ----------------
        st.markdown("### ⏱️ Performance Features")
        pcol1, pcol2, pcol3, pcol4 = st.columns(4)
        pcol1.metric(" Normal Time", f"{st.session_state['normal_time']:.2f} sec")
        pcol2.metric(" Parallel Time", f"{st.session_state['parallel_time']:.2f} sec", 
                     delta=f"-{st.session_state['normal_time'] - st.session_state['parallel_time']:.2f} sec")
        pcol3.metric("⚙️ Actual Execution Time", f"{st.session_state['parallel_time']:.2f} sec")
        pcol4.metric("💻 Cores Used", os.cpu_count() or 4)

        total_score = results_df["Sentiment Score"].sum()
        if total_score >= 10: overall = "Strong Positive"
        elif total_score > 0: overall = "Positive"
        elif total_score <= -10: overall = "Strong Negative"
        elif total_score < 0: overall = "Negative"
        else: overall = "Neutral"
        st.info(f"🏆 **Final Aggregated Sentiment Score:** {total_score} ({overall})")

        speed = total / st.session_state["parallel_time"] if total > 0 and st.session_state["parallel_time"] > 0 else 0
        st.metric("⚡ Processing Speed (rows/sec)", f"{speed:.2f}")

        sentiment_counts = results_df["Sentiment"].value_counts()
        st.subheader("📊 Bar Chart")
        st.bar_chart(sentiment_counts)

        st.subheader("🥧 Pie Chart")
        fig, ax = plt.subplots()
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%')
        st.pyplot(fig)

        st.subheader(" Processed Data Preview")
        st.dataframe(results_df.head(50), use_container_width=True)

    else:
        st.warning("No data processed yet")

# ---------------- SEARCH ----------------
elif st.session_state["nav"] == "search":
    st.subheader("🔍 Search")
    if "results_df" in st.session_state:
        results_df = st.session_state["results_df"]
        keyword = st.text_input("Enter keyword (Supports FTS5 query syntax)", key="search_box")
        if keyword:
            try:
                # Use FTS5 from database
                db_results = search_reviews_fts(keyword)
                if db_results:
                    st.success(f"Found {len(db_results)} results in database (Showing top 1000)")
                    search_df = pd.DataFrame(db_results[:1000], columns=["Text", "Sentiment", "Score", "Source", "Date"])
                    st.dataframe(search_df, use_container_width=True)
                else:
                    st.warning("No matches found in database.")
            except Exception as e:
                # Fallback to local DF search if FTS fails or is empty
                keywords = keyword.lower().split()
                filtered = results_df[
                    results_df["Text"].apply(lambda x: all(k in x.lower() for k in keywords))
                ]
                if len(filtered) > 0:
                    st.success(f"Found {len(filtered)} results (Session Search)")
                    st.dataframe(filtered)
                else:
                    st.warning(f"No matches found. (Error: {str(e)})")
    else:
        st.info("Showing results from entire database history:")
        keyword = st.text_input("Enter keyword to search history", key="search_box_hist")
        if keyword:
            db_results = search_reviews_fts(keyword)
            if db_results:
                search_df = pd.DataFrame(db_results, columns=["Text", "Sentiment", "Score", "Source", "Date"])
                st.dataframe(search_df, use_container_width=True)
            else:
                st.warning("No results found.")

# ---------------- EXPORT ----------------
elif st.session_state["nav"] == "export":
    st.subheader("📤 Export")
    if "results_df" in st.session_state:
        results_df = st.session_state["results_df"]
        csv = results_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "results.csv", "text/csv")
    else:
        st.warning("No data to export")

# ---------------- MANUAL INPUT ----------------
elif st.session_state["nav"] == "manual":
    st.subheader("✍️ Manual Text Analysis")
    user_text = st.text_area("Enter text to analyze manually:", height=150)
    
    if st.button("Analyze Text"):
        if user_text.strip() != "":
            res = analyze_text(user_text)
            st.success("✅ Analysis Complete")
            
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            mcol1.metric("Sentiment", res["sentiment"])
            mcol2.metric("Score", res["score"])
            mcol3.metric("Positive Count", res["pos_count"])
            mcol4.metric("Negative Count", res["neg_count"])
        else:
            st.warning("Please enter some text to analyze.")

# ---------------- HISTORY ----------------
elif st.session_state["nav"] == "history":
    st.subheader("📜 Processing History")
    
    st.info("Showing the most recent 1,000 records from the database.")
    db_data = fetch_all(limit=1000)
    if db_data:
        history_df = pd.DataFrame(db_data, columns=["ID", "Text", "Sentiment", "Score", "Source", "Date"])
        
        # Filters
        hcol1, hcol2 = st.columns(2)
        source_filter = hcol1.multiselect("Filter by Source", options=history_df["Source"].unique())
        sentiment_filter = hcol2.multiselect("Filter by Sentiment", options=history_df["Sentiment"].unique())
        
        filtered_history = history_df
        if source_filter:
            filtered_history = filtered_history[filtered_history["Source"].isin(source_filter)]
        if sentiment_filter:
            filtered_history = filtered_history[filtered_history["Sentiment"].isin(sentiment_filter)]
            
        st.dataframe(filtered_history, use_container_width=True)
        
        # Analytics on history
        