import string

positive_rules = {
    "win":2, "success":2, "award":2, "benefit":1, "growth":2, 
    "improve":1, "popular":1, "respect":1, "great":2, 
    "excellent":3, "happy":2, "best":2, "improved":2, 
    "increase":1, "progress":2, "strong":1, "development":1, "good": 1,
    "positive": 2, "amazing": 3, "wonderful": 3, "fantastic": 3, "love": 2, "incredible": 3, "superb": 3
}

negative_rules = {
    "attack":-2, "war":-2, "crash":-2, "killed":-2, "defeat":-1, 
    "assaulted":-2, "crime":-2, "conflict":-2, "tear":-1, "gas":-1, 
    "bad":-1, "problem":-1, "worst":-3, "fail":-2, "sad":-2, 
    "decline":-2, "death":-1, "crisis":-3, "violence":-3,
    "loss":-2, "damage":-2, "risk":-1,
    "terrible": -3, "negative": -2, "awful": -3, "horrible": -3, "poor": -1, "disappointed": -2, "hate": -2
}

NEGATION_WORDS = {"not", "no", "never", "doesn't", "isn't", "wasn't"}
INTENSITY_MODIFIERS = {"very", "extremely", "highly", "really", "so"}

def analyze_text(review):
    if isinstance(review, list):
        text = " ".join(review).lower()
    else:
        text = str(review).lower()

    words = [word.strip(string.punctuation) for word in text.split()]

    score = 0
    pos_count = 0
    neg_count = 0

    i = 0
    while i < len(words):
        word = words[i]
        
        multiplier = 1
        is_negated = False
        
        # Accumulate adjacent modifiers
        while i < len(words):
            if words[i] in NEGATION_WORDS:
                is_negated = not is_negated
                i += 1
            elif words[i] in INTENSITY_MODIFIERS:
                multiplier *= 2
                i += 1
            else:
                break
                
        if i >= len(words):
            break
            
        word = words[i]

        word_score = 0
        
        if word in positive_rules:
            word_score = positive_rules[word] * multiplier
            if is_negated:
                word_score = -word_score
                neg_count += 1
            else:
                pos_count += 1
                
        elif word in negative_rules:
            word_score = negative_rules[word] * multiplier
            if is_negated:
                word_score = -word_score
                pos_count += 1
            else:
                neg_count += 1

        score += word_score
        i += 1

    # Determine final compound sentiment
    if score >= 2:
        sentiment = "Strong Positive"
    elif score > 0:
        sentiment = "Positive"
    elif score <= -2:
        sentiment = "Strong Negative"
    elif score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "score": score,
        "pos_count": pos_count,
        "neg_count": neg_count
    }