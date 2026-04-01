from rule_engine import analyze_text

def test_sentiment():
    test_cases = {
        "terrible": "Negative",
        "amazing": "Positive",
        "neutral": "Neutral",
        "positive": "Positive",
        "negative": "Negative",
        "This is a wonderful day!": "Positive",
        "I hate this terrible problem.": "Negative"
    }
    
    print("--- Sentiment Analysis Test ---")
    all_passed = True
    for text, expected in test_cases.items():
        res = analyze_text(text)
        actual = res['sentiment']
        status = "✅" if expected in actual else "❌"
        print(f"Text: '{text}' | Expected contains: {expected} | Actual: {actual} {status}")
        if expected not in actual:
            all_passed = False
            
    if all_passed:
        print("\nAll logical tests passed!")
    else:
        print("\nSome tests failed!")

if __name__ == "__main__":
    test_cases = {
        "terrible": "Strong Negative",
        "amazing": "Strong Positive",
        "neutral": "Neutral",
        "positive": "Strong Positive",
        "negative": "Strong Negative",
        "very good": "Strong Positive",
        "good": "Positive",
        "This is a wonderful day!": "Strong Positive",
        "I hate this terrible problem.": "Strong Negative"
    }
    
    print("--- Sentiment Analysis Test ---")
    for text, expected in test_cases.items():
        res = analyze_text(text)
        actual = res['sentiment']
        print(f"Text: '{text}' -> {actual} (Score: {res['score']})")

    # Specifically check 'terrible'
    res = analyze_text("terrible")
    if "Negative" in res['sentiment']:
        print("\nSUCCESS: 'terrible' is now negative.")
    else:
        print("\nFAILURE: 'terrible' is still not negative.")
